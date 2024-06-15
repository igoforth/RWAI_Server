import asyncio
import os
import sys
from pathlib import Path
from time import time

import aiofiles
import openai
import polib

# Set up OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
client = openai.AsyncOpenAI(api_key=api_key)

# Directory structure and language details
LOCALES_DIR = Path("locales")
SOURCE_LANGUAGE = "en"

# Define the rate limit (requests per minute)
REQUESTS_PER_MINUTE = 4000
REQUEST_INTERVAL = 60.0 / REQUESTS_PER_MINUTE
semaphore = asyncio.Semaphore(REQUESTS_PER_MINUTE)
last_request_time = 0


# Function to translate text using OpenAI API with rate limiting
async def translate_text(text: str, target_language: str) -> str:
    global last_request_time
    async with semaphore:
        current_time = time()
        elapsed_time = current_time - last_request_time
        if elapsed_time < REQUEST_INTERVAL:
            await asyncio.sleep(REQUEST_INTERVAL - elapsed_time)

        last_request_time = time()

        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a Translator. For a given input text, output ONLY the {target_language} equivalent.\n\nFrench Example:\n\nInput:\nYou are a technical writer. Summarize the $num most relevant nodes from the provided XML to pass on to creative writers.\n\nOutput:\nVous êtes rédacteur technique. Résumez les $num nœuds les plus pertinents du XML fourni pour les transmettre aux rédacteurs créatifs.",
                    },
                    {"role": "user", "content": text},
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error translating text: {e}", file=sys.stderr)
            return text  # Fallback to original text on error


# Process a single .po file
async def process_po_file(po_file: Path, target_language: str, indices_to_redo=None):
    try:
        po = polib.pofile(str(po_file))
    except Exception as e:
        print(f"Error reading .po file {po_file}: {e}", file=sys.stderr)
        return

    tasks = []
    for idx, entry in enumerate(po):
        if indices_to_redo is None or idx in indices_to_redo:
            tasks.append((entry, translate_text(entry.msgid, target_language)))

    results = await asyncio.gather(*[task[1] for task in tasks])
    for (entry, _), translation in zip(tasks, results):
        entry.msgstr = translation

    async with aiofiles.open(po_file, "w", encoding="utf-8") as f:
        await f.write(str(po))


# Process all .po files in the directory
async def process_all_po_files(locales_dir: Path):
    tasks = []
    for lang_dir in locales_dir.iterdir():
        if lang_dir.is_dir() and lang_dir.name != SOURCE_LANGUAGE:
            target_language = lang_dir.name
            for po_file in lang_dir.rglob("*.po"):
                tasks.append(process_po_file(po_file, target_language))
    await asyncio.gather(*tasks)


# Redo translations for specific languages and indices
async def redo_translations(language: str, indices: list[int]):
    lang_dir = LOCALES_DIR / language
    if lang_dir.is_dir() and language != SOURCE_LANGUAGE:
        for po_file in lang_dir.rglob("*.po"):
            await process_po_file(po_file, language, indices)


# Main entry point
if __name__ == "__main__":
    # Example usage: redo translations for French language, indices 0 and 2
    # asyncio.run(redo_translations("fr", [1, 2]))

    # Process all files
    asyncio.run(process_all_po_files(LOCALES_DIR))
