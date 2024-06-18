# pdm run pybabel init -i locales/messages.pot -d locales -l uk

import subprocess
from pathlib import Path


def compile_translations(locales_dir: str):
    language_codes = [
        "ar",  # Arabic
        "zh_Hans",  # Chinese Simplified
        "zh_Hant",  # Chinese Traditional
        "cs",  # Czech
        "da",  # Danish
        "nl",  # Dutch
        "en",  # English
        "et",  # Estonian
        "fi",  # Finnish
        "fr",  # French
        "de",  # German
        "hu",  # Hungarian
        "it",  # Italian
        "ja",  # Japanese
        "ko",  # Korean
        "no",  # Norwegian
        "pl",  # Polish
        "pt",  # Portuguese
        "pt_BR",  # Portuguese Brazilian
        "ro",  # Romanian
        "ru",  # Russian
        "sk",  # Slovak
        "es",  # Spanish
        "es_419",  # Spanish Latin America
        "sv",  # Swedish
        "tr",  # Turkish
        "uk",  # Ukrainian
    ]

    for lang in language_codes:
        pot_path = Path(locales_dir) / "messages.pot"

        subprocess.run(
            [
                "pdm",
                "run",
                "pybabel",
                "init",
                "-i",
                str(pot_path),
                "-d",
                str(locales_dir),
                "-l",
                lang,
            ]
        )


if __name__ == "__main__":
    locales_dir = "locales"
    compile_translations(locales_dir)
