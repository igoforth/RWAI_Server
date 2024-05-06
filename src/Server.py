import os
import platform
import subprocess
import asyncio

from grpclib.utils import graceful_exit
from grpclib.server import Server

AI_SERVER_REPO_URL = "https://github.com/igoforth/AIServer.git"
ARCH = platform.architecture()[0]
OS = platform.system()
RWAI_WORKSPACE = os.getcwd()

def verify() -> list[str]
    error_list = []
    error_bool = False
    
    # confirm git is installed
    if subprocess.run(["git", "--version"]).returncode != 0:
        print("Git is not installed: fatal")
        error_list.append("git")
        error_bool = True
        
    if error_bool:
        return error_list
    
    # confirm curl is installed
    if subprocess.run(["curl", "--version"]).returncode != 0:
        print("Curl is not installed")
        error_list.append("curl")
        error_bool = True
        
    if error_bool:
        return error_list





def main():
    print("Hello World")
    verify()

if __name__ == "__main__":
    main()