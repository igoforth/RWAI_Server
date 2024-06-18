import os
import subprocess
from pathlib import Path


def compile_translations(locales_dir: str, output_dir: str):
    languages = [
        d
        for d in os.listdir(locales_dir)
        if os.path.isdir(os.path.join(locales_dir, d))
    ]

    for lang in languages:
        po_path = Path(locales_dir) / lang / "LC_MESSAGES" / "messages.po"
        mo_path = Path(output_dir) / lang / "LC_MESSAGES" / "messages.mo"

        mo_dir = mo_path.parent
        if not mo_dir.exists():
            os.makedirs(mo_dir)

        subprocess.run(
            [
                "pdm",
                "run",
                "pybabel",
                "compile",
                "-i",
                str(po_path),
                "-o",
                str(mo_path),
                "-l",
                lang,
                "-f",
            ]
        )


if __name__ == "__main__":
    locales_dir = "locales"
    output_dir = "src/AIServer/locales"
    compile_translations(locales_dir, output_dir)
