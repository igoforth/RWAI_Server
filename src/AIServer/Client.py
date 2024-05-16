import asyncio
from string import Template
from time import monotonic
from urllib.parse import urljoin

import httpx
import openai_python_client

from .__init__ import logger
from .Health import AIHealth

DEFAULT_PROMPT: Template = Template(r"""<|user|>\nYou are the world's best creative writer assigned to work on the popular game called RimWorld.\n\nA Rimworld is a planet lacking a strong central government and has a sparse population. These places tend to hover around the industrial level of technology or lower. Because they’re not homogenized by a central government, they tend to see a lot of interaction between people of different technology levels, as travelers crash-land or ancient communities stumble out of their cryptosleep vaults. These planets are often at the rim of known space, hence the name.\n\nYour task is to come up with descriptions for items found in-game. There are millions of possible items, so your work is cut out for you. I'll give you the information I have in XML, and you create a backstory that fits it! Aim for a five sentence description surrounded in quotes. Here you go:\n\n<saveable Class="Building_Art">\n  <id>SculptureGrand15070</id>\n  <pos>(60,0,66)</pos>\n  <map>0</map>\n  <health>195</health>\n  <stuff>WoodLog</stuff>\n  <faction>Faction_14</faction>\n  <questTags IsNull="True" />\n  <spawnedTick>59</spawnedTick>\n  <quality>Masterwork</quality>\n  <sourcePrecept>null</sourcePrecept>\n  <everSeenByPlayer>True</everSeenByPlayer>\n  <tile>0</tile>\n  <art>Son</art>\n  <seed>533422075</seed>\n  <taleRef>null</taleRef>\n</saveable>\n\nOriginal Description: "This sculpture bears a portrayal of a thresher suspended in the air surrounded by devils. A goshawk stands beneath the main subject. The overall composition is well balanced."<|end|>\n<|assistant|>Sure! Here is your description: " """.strip())

# ARGS
HOST = '127.0.0.1'
PORT = 50052

class AIClient:
    def __init__(self, srv_host: str, srv_port: int):
        self.srv_host: str = srv_host
        self.srv_port: int = srv_port
        self.srv_url: str = f"http://{self.srv_host}:{self.srv_port}"
        self.client: openai_python_client.Client = openai_python_client.Client(base_url=self.srv_url)
        self.health_interval: int = 15
        self.ai_health = AIHealth.UNKNOWN

    async def start(self, input_queue: asyncio.Queue, output_queue: asyncio.Queue, max_sleep: float = 0.1) -> None:
        last_time: float = monotonic()
        sleep_for: float = max_sleep
        while True:
            # Get a "work item" out of the queue.
            try:
                work_item, sleep_for = await input_queue.get_nowait()
                
                # do work

                # Notify the queue that the "work item" has been processed.
                input_queue.task_done()
            except asyncio.QueueEmpty:
                pass
            
            # If time difference between this check and last check is more than the set interval
            # then check health
            cur_time: float = monotonic()
            if cur_time - last_time > self.health_interval:
                last_time = cur_time
                await self.CheckAIHealth()
            
            # Sleep for the "sleep_for" seconds or max_sleep, whichever is less
            await asyncio.sleep(min(sleep_for, max_sleep))
            # logger.debug(f'{repr(self)} has slept for {sleep_for:.2f} seconds')

    # GET /health: Returns the current state of the server:
    # * {"status": "loading model"} if the model is still being loaded.
    # * {"status": "error"} if the model failed to load.
    # * {"status": "ok"} if the model is successfully loaded and the server is ready for further requests mentioned below.
    async def CheckAIHealth(self) -> None:
        client = self.client.get_async_httpx_client()
        try:
            r = await client.get(url=urljoin(self.srv_url, "/health"),  timeout=5)
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
        except httpx.TimeoutException:
            logger.error("HealthCheck: TimeoutException")
            self.ai_health = AIHealth.OFFLINE


async def run(input_queue: asyncio.Queue, output_queue: asyncio.Queue):
    client = None
    try:
        client = AIClient(HOST, PORT)
        await client.start(input_queue, output_queue, max_sleep=1)
        logger.info(f'Client connected to {HOST}:{PORT}')
    except asyncio.CancelledError: 
        if client:
            await client.client.get_async_httpx_client().aclose()
        logger.info("Client gracefully shut down")