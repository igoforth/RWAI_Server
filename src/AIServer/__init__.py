import asyncio
import logging
import pathlib
import platform
import signal
import sys
import traceback
from collections import deque
from time import monotonic

logger  = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# add to path "FILE/../../../__pypackages__/VERSION_SHORT/lib"
mjr_mnr = ".".join(platform.python_version_tuple()[:2])
new_path = str(pathlib.Path(__file__).parent.parent.parent / pathlib.Path(f"__pypackages__/{mjr_mnr}/lib"))
sys.path.append(new_path)

import Client
# import Health
import Server

MAX_INTERVAL = 30
RETRY_HISTORY = 3
LLAMAFILE_EXE: str = "bin/llamafile"
LLAMAFILE_PARAMS_LIST: list[str] = [
    "--host", "127.0.0.1", "--port", "50052",
    "-ngl", "9999", "--server", "--nobrowser", "-cb",
    "-m", "models/Phi-3-mini-128k-instruct.Q4_K_M.gguf",
    "--chat-template", r""" "{{ bos_token }}{% for message in messages %}{% if (message['role'] == 'user') %}{{'<|user|>' + '\n' + message['content'] + '<|end|>' + '\n' + '<|assistant|>' + '\n'}}{% elif (message['role'] == 'assistant') %}{{message['content'] + '<|end|>' + '\n'}}{% endif %}{% endfor %}" """.strip()
]

async def run_forever(program: str, args: list[str], sleep_interval: int):
    """Capture output (stdout and stderr) while running external command."""
    proc = await asyncio.create_subprocess_exec(
        program, *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    while True:
        if proc.stdout.at_eof() and proc.stderr.at_eof():
            break

        stdout = (await proc.stdout.readline()).decode()
        if stdout:
            logger.debug(f'[stdout] {stdout}', end='', flush=True)
        stderr = (await proc.stderr.readline()).decode()
        if stderr:
            logger.debug(f'[sdterr] {stderr}', end='', flush=True, file=sys.stderr)

        await asyncio.sleep(sleep_interval)

    await proc.communicate()

    logger.info(f'{program} {" ".join(args)} exited with {proc.returncode}')

def supervise(loop: asyncio.BaseEventLoop, func, name=None, retry_history=RETRY_HISTORY, max_interval=MAX_INTERVAL):
    """Simple wrapper function that automatically tries to name tasks"""
    if name is None:
        if hasattr(func, '__name__'): # raw func
            name = func.__name__
        elif hasattr(func, 'func'): # partial
            name = func.func.__name__
    return loop.create_task(supervisor(func, retry_history, max_interval), name=name)

async def supervisor(func, retry_history=RETRY_HISTORY, max_interval=MAX_INTERVAL):
    """Takes a noargs function that creates a coroutine, and repeatedly tries
        to run it. It stops is if it thinks the coroutine is failing too often or
        too fast.
    """
    start_times = deque([float('-inf')], maxlen=retry_history)
    while True:
        start_times.append(monotonic())
        try:
            return await func()
        except Exception:
            if min(start_times) > monotonic() - max_interval:
                logger.critical(
                    f'Failure in task {asyncio.current_task().get_name()!r}.'
                    ' Is it in a restart loop?'
                )
                # we tried our best, this coroutine really isn't working.
                # We should try to shutdown gracefully by setting a global flag
                # that other coroutines should periodically check and stop if they
                # see that it is set. However, here we just reraise the exception.
                raise
            else:
                logger.error(func.__name__, 'failed, will retry. Failed because:')
                traceback.print_exc()

def main():

    class GracefulExit(SystemExit):
        code = 1

    def raise_graceful_exit(*args):
        tasks = asyncio.all_tasks(loop=loop)
        for t in tasks:
            t.cancel()

        loop.stop()
        raise GracefulExit()

    # health_watcher = Health.HealthWatcher()
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()

    loop = asyncio.get_event_loop()
    signal.signal(signal.SIGINT,  raise_graceful_exit)
    signal.signal(signal.SIGTERM, raise_graceful_exit)
    supervise(loop, run_forever(LLAMAFILE_EXE, LLAMAFILE_PARAMS_LIST, sleep_interval = 5))
    supervise(loop, Server.run(input_queue, output_queue))
    supervise(loop, Client.run(input_queue, output_queue))
    tasks = asyncio.all_tasks(loop=loop)
    group = asyncio.gather(*tasks, return_exceptions=True)

    try:
        loop.run_until_complete(group)
    except GracefulExit:
        print('Got signal: SIGINT, shutting down.')
    if 1:
        for t in tasks:
            t.cancel()
        loop.run_until_complete(group)
        loop.close()