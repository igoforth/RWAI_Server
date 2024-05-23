import asyncio
import functools
import logging
import os
import pathlib
import platform
import signal
import sys
import traceback
from collections import deque
from time import monotonic

os_name, os_release, os_version = (
    platform.system(),
    platform.release(),
    platform.version(),
)

# logging
logger = logging.getLogger(__name__)
# if (logger.hasHandlers()):
#     logger.handlers.clear()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logger.getEffectiveLevel())
stderr_handler.setFormatter(formatter)
logger.addHandler(stderr_handler)
logger.propagate = False

# add to path "FILE/../../../__pypackages__/VERSION_SHORT/lib"
mjr_mnr = ".".join(platform.python_version_tuple()[:2])
new_path = str(
    pathlib.Path(__file__).parent.parent.parent
    / pathlib.Path(f"__pypackages__/{mjr_mnr}/lib")
)
sys.path.append(new_path)
# import Health
from . import Client, Server

MAX_INTERVAL = 30
RETRY_HISTORY = 3


def get_largest_file(directory: pathlib.Path) -> pathlib.Path:
    # Initialize variables to store the name and size of the largest file
    largest_file = pathlib.Path()
    largest_size = 0

    # Iterate over all files in the provided directory
    for file in pathlib.Path(directory).rglob("*"):
        if file.is_file():  # Ensure it is a file
            file_size = file.stat().st_size

            # Check if the current file is the largest so far
            if file_size > largest_size:
                largest_size = file_size
                largest_file = file

    return largest_file


# ARGS
LLAMAFILE_FILENAME = "llamafile.com" if os_name == "Windows" else "llamafile"
LLAMAFILE_PATH: pathlib.Path = pathlib.Path(os.getcwd()) / "bin" / LLAMAFILE_FILENAME
LLAMAFILE_MODEL: pathlib.Path = get_largest_file(
    pathlib.Path(os.getcwd()) / "models"
).relative_to(pathlib.Path(os.getcwd()))
LLAMAFILE_PARAMS_LIST: list[str] = [
    "--host",
    "127.0.0.1",
    "--port",
    "50052",
    "-ngl",
    "9999",
    "--server",
    "--nobrowser",
    "-cb",
    "-m",
    str(LLAMAFILE_MODEL),
    "--chat-template",
    r""" "{{ bos_token }}{% for message in messages %}{% if (message['role'] == 'user') %}{{'<|user|>' + '\n' + message['content'] + '<|end|>' + '\n' + '<|assistant|>' + '\n'}}{% elif (message['role'] == 'assistant') %}{{message['content'] + '<|end|>' + '\n'}}{% endif %}{% endfor %}" """.strip(),
]


async def run_llama_forever():
    """Capture output (stdout and stderr) while running external command."""
    stderr_filepath = pathlib.Path("llama_stderr.log")
    if stderr_filepath.exists():
        stderr_filepath.unlink()
    else:
        stderr_filepath.touch()
    stderr_file = open(stderr_filepath, "wb")
    proc = await asyncio.create_subprocess_exec(
        LLAMAFILE_PATH,
        *LLAMAFILE_PARAMS_LIST,
        stdout=asyncio.subprocess.PIPE,
        stderr=stderr_file,
    )

    try:
        while True:
            if proc.stdout.at_eof() and proc.stderr.at_eof():
                break

            try:
                out = await asyncio.wait_for(proc.stdout.read(2048), 0.1)
            except asyncio.TimeoutError:
                pass
            else:
                logger.debug(f"[AI Server] {out.decode().strip()}")
            # try:
            #     err = await asyncio.wait_for(proc.stderr.read(2048), 0.1)
            # except asyncio.TimeoutError:
            #     pass
            # else:
            #     logger.debug(f"[stderr] {err.decode().strip()}")

    except asyncio.CancelledError:
        logger.info("AI gracefully shut down")
    finally:
        await proc.communicate()
        stderr_file.close()
        # logger.debug(f'{LLAMAFILE_PATH} {" ".join(LLAMAFILE_PARAMS_LIST)} exited with {proc.returncode}')


def supervise(func, name=None, retry_history=RETRY_HISTORY, max_interval=MAX_INTERVAL):
    """Simple wrapper function that automatically tries to name tasks"""
    if name is None:
        if hasattr(func, "__name__"):  # raw func
            name = func.__name__
        elif hasattr(func, "func"):  # partial
            name = func.func.__name__
    return asyncio.create_task(
        supervisor(func, name, retry_history, max_interval), name=name
    )


async def supervisor(
    func, name, retry_history=RETRY_HISTORY, max_interval=MAX_INTERVAL
):
    """Takes a noargs function that creates a coroutine, and repeatedly tries
    to run it. It stops is if it thinks the coroutine is failing too often or
    too fast."""
    start_times = deque([float("-inf")], maxlen=retry_history)
    while True:
        start_times.append(monotonic())
        try:
            return await func()
        except Exception:
            if min(start_times) > monotonic() - max_interval:
                logger.critical(
                    f"Failure in task {asyncio.current_task().get_name()!r}."
                    " Is it in a restart loop?"
                )
                # we tried our best, this coroutine really isn't working.
                # We should try to shutdown gracefully by setting a global flag
                # that other coroutines should periodically check and stop if they
                # see that it is set. However, here we just reraise the exception.
                raise
            else:
                logger.error(name, "failed, will retry. Failed because:")
                traceback.print_exc()


class GracefulExit(SystemExit):
    code = 1


def raise_graceful_exit(*args):
    raise GracefulExit()


async def main_async(iq, oq):
    tasks = [
        supervise(run_llama_forever),
        supervise(functools.partial(Server.run, iq, oq)),
        supervise(functools.partial(Client.run, iq, oq)),
    ]
    await asyncio.wait(
        tasks,
        # Only stop when all coroutines have completed
        # -- this allows for a graceful shutdown
        # Alternatively use FIRST_EXCEPTION to stop immediately
        return_when=asyncio.ALL_COMPLETED,
    )
    return tasks


def main():
    iq = asyncio.Queue()
    oq = asyncio.Queue()

    # health_watcher = Health.HealthWatcher()

    loop = asyncio.get_event_loop()
    signal.signal(signal.SIGINT, raise_graceful_exit)
    signal.signal(signal.SIGTERM, raise_graceful_exit)

    try:
        tasks = asyncio.ensure_future(main_async(iq, oq), loop=loop)
        loop.run_until_complete(tasks)
    except GracefulExit:
        logger.info("Got signal: SIGINT, shutting down.")
    finally:
        tasks = asyncio.all_tasks(loop=loop)
        for t in tasks:
            t.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()
