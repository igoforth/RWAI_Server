import json
import os
import subprocess
import sys

assert len(sys.argv) >= 2
[_, pattern, *rest] = sys.argv

print(subprocess.check_output(
    [
        "pypack1",
        os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "json-schema-to-grammar.py"),
        *rest,
        "-",
        "--raw-pattern",
    ],
    text=True,
    input=json.dumps({
        "type": "string",
        "pattern": pattern,
    }, indent=2)))
