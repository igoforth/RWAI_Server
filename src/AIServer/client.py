from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from asyncio import CancelledError, Queue, QueueEmpty, sleep
from urllib.parse import urljoin
from zipfile import ZipFile

import httpx
import openai_python_client.api.chat.create_chat_completion as api
from openai_python_client import Client
from openai_python_client.models.user_message import UserMessage
from openai_python_client.models.user_message_role import UserMessageRole

from .__init__ import LLAMAFILE_MODEL, LLAMAFILE_SIZE, logger
from .health import AIHealth

# generated by protoc
from .job.job_pb2 import JobRequest, JobResponse, SupportedLanguage
from .templates import trans_manager

# ARGS
HOST = "127.0.0.1"
PORT = 50052


class AIClient:
    def __init__(self, srv_host: str, srv_port: int):
        self.srv_host: str = srv_host
        self.srv_port: int = srv_port
        self.srv_url: str = f"http://{self.srv_host}:{self.srv_port}/v1"
        self.health_interval: int = 15
        self.ai_health = AIHealth.UNKNOWN
        self.grammar_quotes: str = (
            ZipFile(sys.argv[0]).read("AIServer/schemas/quote.gbnf").decode("utf-8")
        )
        self.grammar_digit: str = (
            ZipFile(sys.argv[0]).read("AIServer/schemas/digit.gbnf").decode("utf-8")
        )
        self.grammar_yesno: str = (
            ZipFile(sys.argv[0]).read("AIServer/schemas/yesno.gbnf").decode("utf-8")
        )

    async def test_art_description_job(self) -> None:
        language: SupportedLanguage = SupportedLanguage.CHINESE_SIMPLIFIED
        hash_code: int = 0
        xml_def: str = (
            r"""
<saveable Class="Building_Art">
  <id>SculptureGrand5070</id>
  <pos>(60,0,66)</pos>
  <map>0</map>
  <health>195</health>
  <stuff>WoodLog</stuff>
  <faction>Faction14</faction>
  <questTags IsNull="True" />
  <spawnedTick>59</spawnedTick>
  <quality>Masterwork</quality>
  <sourcePrecept>null</sourcePrecept>
  <everSeenByPlayer>True</everSeenByPlayer>
  <tile>0</tile>
  <art>Son</art>
  <seed>533422075</seed>
  <taleRef>null</taleRef>
</saveable>
""".strip()
        )
        title: str = ""
        description: str = ""
        job: JobRequest.ArtDescriptionJob = JobRequest.ArtDescriptionJob(
            hash_code=hash_code,
            xml_def=xml_def,
            title=title,
            description=description,
        )
        await self.do_art_description_job(job, language=language)

    async def start(
        self,
        input_queue: Queue[tuple[int, JobRequest]],
        output_queue: Queue[tuple[int, JobResponse]],
    ) -> None:
        sleep_for: float = 0.5

        while True:
            try:
                request_job_id: int
                request: JobRequest

                # Get a "work item" out of the queue.
                request_job_id, request = input_queue.get_nowait()

                # switch supported request types
                response: JobResponse = JobResponse()
                response.job_id = request_job_id
                match request.WhichOneof("job_payload"):  # type: ignore
                    case "art_description_job":
                        art_description_response = await self.do_art_description_job(
                            request.art_description_job,
                            request.language,
                        )
                        response.art_description_response.CopyFrom(  # type: ignore
                            art_description_response
                        )
                    case _:  # type: ignore
                        pass

                # Put the result into the output queue
                await output_queue.put((response.job_id, response))
            except QueueEmpty:
                # Sleep for the "sleep_for" seconds
                await sleep(sleep_for)

    async def do_art_description_length(self, xml_def: str) -> tuple[int, str]:
        # Load language-specific templates
        try:
            # Parse XML and extract definitions
            xml_def_et = ET.fromstring(xml_def)
            defin = xml_def_et.findtext("def", default="Art")
            stuff = xml_def_et.findtext("stuff", default="Steel")
            quality = xml_def_et.findtext("quality", default="Good")

            # Generate description using templates
            short_desc_template = trans_manager.get_template("short_t")
            short_desc = short_desc_template.substitute(
                defin=defin,
                stuff=stuff,
                quality=quality,
            )
        except ET.ParseError:
            short_desc = "Type: Art\nMaterial: Steel\nQuality: Good"
            print("Failed to parse XML definition.", file=sys.stderr)

        # Retrieve story length
        length_msg_template = trans_manager.get_template("length_t")
        message = length_msg_template.substitute(info=short_desc)
        reply: str | None = await self.do_chat(message, grammar=self.grammar_digit)
        return int(reply.strip()) if reply and reply.isdigit() else 4, short_desc

    async def do_art_description_story(
        self,
        language: SupportedLanguage,
        story_len: int,
        title: str,
        short_desc: str,
        description: str,
    ) -> str:
        # Generate story based on the size configuration
        story_template_key = (
            f"story_{'mini' if LLAMAFILE_SIZE is None else LLAMAFILE_SIZE}_t"
        )
        # the below languages are not well supported by the tokenizer, so we must use the "small" description if using the "medium" model
        if LLAMAFILE_SIZE == "medium" and language in [
            SupportedLanguage.RUSSIAN,
            SupportedLanguage.KOREAN,
            SupportedLanguage.UKRAINIAN,
            SupportedLanguage.HUNGARIAN,
            SupportedLanguage.JAPANESE,
        ]:
            story_template_key = "story_small_t"
        story_template = trans_manager.get_template(story_template_key)
        story_msg = story_template.substitute(
            len=story_len,
            title=title,
            description=short_desc + "\n\n" + description,
        )
        return await self.do_chat(story_msg, grammar=self.grammar_quotes) or description

    async def do_art_description_name(self, title: str, story: str) -> str:
        # Determine name
        name_template = trans_manager.get_template("name_t")
        name_msg = name_template.substitute(pas=story)
        return await self.do_chat(name_msg, grammar=self.grammar_quotes) or title

    async def do_art_description_job(
        self,
        art_job: JobRequest.ArtDescriptionJob,
        language: SupportedLanguage,
    ) -> JobResponse.ArtDescriptionResponse:
        hash_code: int = art_job.hash_code
        title: str = art_job.title
        description: str = art_job.description
        xml_def: str = art_job.xml_def

        # Set language
        trans_manager.set_locale(language)

        # Determine length
        story_len, short_desc = await self.do_art_description_length(xml_def)

        # Determine story
        story = await self.do_art_description_story(
            language,
            story_len,
            title,
            short_desc,
            description,
        )

        # Strip quotes from story
        new_story: str | None = await self.validate_art_description_story(story)
        tries: int = 5
        while new_story == None:
            new_story = await self.validate_art_description_story(
                await self.do_art_description_story(
                    language, story_len, title, short_desc, description
                )
            )
            tries -= 1
            if tries == 0:
                new_story = story
                break
        story = new_story

        # Determine name
        name = await self.do_art_description_name(title, story)

        # Strip quotes from name
        new_name: str | None = self.extract_quoted_string(name)
        tries: int = 5
        while new_name == None:
            new_name = self.extract_quoted_string(
                await self.do_art_description_name(title, story)
            )
            tries -= 1
            if tries == 0:
                new_name = name
                break
        name = new_name

        # Replace all mentions of the old title with the new title in the story
        story = story.replace(title, name).strip()

        # Return result
        return JobResponse.ArtDescriptionResponse(
            hash_code=hash_code,
            xml_def=xml_def,
            title=name,
            description=story,
        )

    async def do_chat(
        self, content: str, grammar: str | None = None, fallback: int | None = None
    ) -> str:
        message: UserMessage = UserMessage(
            role=UserMessageRole.USER,
            content=content.strip(),
        )
        request: api.CreateChatCompletionRequest = api.CreateChatCompletionRequest(
            messages=[message],
            model=str(LLAMAFILE_MODEL),
            temperature=0.7,
        )

        # additional properties
        if grammar:
            request.additional_properties["grammar"] = grammar
        request.additional_properties["dynatemp_range"] = 0.3
        request.additional_properties["repeat_penalty"] = 1.05
        request.additional_properties["stop"] = (
            [  # conditions which should cause the model to stop generating, normal or abnormal
                "<|end|>",
                "<|endoftext|>",
                "<|im_end|>",
                "\n",
                "\r",
                "        ",  # excessive spaces (8 and up)
                "\t\t\t\t",  # excessive tabs (4 and up)
            ]
        )

        logger.debug(f"Request:\n{request.to_dict()}")
        response: api.CreateChatCompletionResponse | None = await api.asyncio(
            client=self.client,
            body=request,
        )
        if not response:
            if fallback:
                if fallback != 0:
                    fallback -= 1
                    return await self.do_chat(content, grammar, fallback)
                else:
                    return ""
            else:
                return ""
        logger.debug(f"Response:\n{response.to_dict()}")
        reply: str | None = response.choices[0].message.content
        if not reply:
            if fallback:
                if fallback != 0:
                    fallback -= 1
                    return await self.do_chat(content, grammar, fallback)
                else:
                    return ""
            else:
                return ""
        if "<|end|>" in reply:
            reply = reply.replace("<|end|>", "")
        if "<|endoftext|>" in reply:
            reply = reply.replace("<|endoftext|>", "")
        if "<|im_end|>" in reply:
            reply = reply.replace("<|im_end|>", "")
        return reply.strip()

    # GET /health: Returns the current state of the server:
    # * {"status": "loading model"} if the model is still being loaded.
    # * {"status": "error"} if the model failed to load.
    # * {"status": "ok"} if the model is successfully loaded and the server is ready for further requests mentioned below.
    async def check_ai_health(self) -> None:
        try:
            self.client: Client = Client(self.srv_url, verify_ssl=False)
            r = await self.client.get_async_httpx_client().get(
                url=urljoin(self.srv_url, "/health"), timeout=5
            )
            if r.status_code == 200:
                json_data = r.json()
                logger.debug(json_data)
                status = json_data.get("status", "")
                if status == "loading model":
                    self.ai_health = AIHealth.STARTING
                elif status == "error":
                    self.ai_health = AIHealth.ERROR
                elif status == "ok":
                    self.ai_health = AIHealth.HEALTHY
                else:
                    self.ai_health = AIHealth.UNKNOWN
            else:
                self.ai_health = AIHealth.ERROR
        except httpx.ConnectError:
            logger.error("HealthCheck: ConnectException")
            self.ai_health = AIHealth.OFFLINE
        except httpx.ReadError:
            logger.error("HealthCheck: ReadException")
            self.ai_health = AIHealth.OFFLINE
        except httpx.TimeoutException:
            logger.error("HealthCheck: TimeoutException")
            self.ai_health = AIHealth.OFFLINE
        # Because we're using a grammar, we can expect something like /^\s*\".*\"\s*$/

    async def validate_art_description_story(self, s: str) -> str | None:
        new_story: str | None = self.extract_quoted_string(s)
        if new_story is None:
            return None
        msg = f"Is the below content cut off at the end? Please answer Yes or No.\n\n{new_story}"
        resp = await self.do_chat(msg, grammar=self.grammar_yesno)
        if resp.strip() == "Yes":
            return None
        return new_story

    @staticmethod
    def extract_quoted_string(s: str) -> str | None:
        import re

        pattern = r"^[ \t]*\"([^\"]+)\"[ \t]*$"
        match = re.match(pattern, s)
        if match:
            return match.group(1)
        return None


async def run(
    input_queue: Queue[tuple[int, JobRequest]],
    output_queue: Queue[tuple[int, JobResponse]],
):
    global client
    client = AIClient(HOST, PORT)
    tries = 0
    try:
        while client.ai_health != AIHealth.HEALTHY:
            if tries == 5:
                raise ConnectionError("Failed 5 times to connect to llamafile")
            await client.check_ai_health()
            tries += 1
            await sleep(5)
        # await client.test_art_description_job()
        logger.info(f"Client connected to {HOST}:{PORT}")
        await client.start(input_queue, output_queue)
    except CancelledError:
        await client.client.get_async_httpx_client().aclose()
        logger.info("Client gracefully shut down")
