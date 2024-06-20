# -*- coding: utf-8 -*-
import dataclasses
import sys

# PEP 441 https://peps.python.org/pep-0441/
# PEP 771 https://peps.python.org/pep-0711/


@dataclasses.dataclass
class PlatformPythonManager:
    import contextlib
    import pathlib
    import typing

    system: str = ""
    machine: str = ""
    os_dir: str = ""
    arch_dir: str = ""

    def __post_init__(self):
        import platform

        self.system = platform.system().lower()
        self.machine = platform.machine().lower()

        if self.system == "linux":
            self.os_dir = "linux"
            self.arch_dir = (
                "x86_64"
                if any(["x86_64" in self.machine, "amd64" in self.machine])
                else (
                    "aarch64"
                    if any(["arm64" in self.machine, "aarch64" in self.machine])
                    else ""
                )
            )
        elif self.system == "darwin":
            self.os_dir = "darwin"
            self.arch_dir = (
                "x86_64"
                if any(["x86_64" in self.machine, "amd64" in self.machine])
                else (
                    "arm64"
                    if any(["arm64" in self.machine, "aarch64" in self.machine])
                    else ""
                )
            )
        elif self.system == "windows":
            self.os_dir = "windows"
            self.arch_dir = (
                "x86_64"
                if any(["x86_64" in self.machine, "amd64" in self.machine])
                else "x86" if "x86" in self.machine else ""
            )

        if self.os_dir == "" or self.arch_dir == "":
            raise RuntimeError(f"Unsupported platform: {self.system} {self.machine}")

    def set_executable_permissions(self, path: pathlib.Path):
        import os
        import pathlib
        import stat

        try:
            if self.system in ["linux", "darwin"]:
                st = os.stat(path)
                os.chmod(path, st.st_mode | stat.S_IEXEC)
                # furthermore, chmod any files under "bin" subdirectories
                for bin in pathlib.Path(path.parent).glob("**/bin/*"):
                    os.chmod(bin, st.st_mode | stat.S_IEXEC)
            elif self.system == "windows":
                if not os.access(path, os.X_OK):
                    os.chmod(path, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
        except Exception as e:
            raise RuntimeError(f"Failed to set executable permissions for {path}: {e}")

    def get_platform_python_bin(self, path: pathlib.Path):
        if self.system in ["linux", "darwin"]:
            path /= "bin/python"
        elif self.system == "windows":
            path /= "python.exe"
        else:
            raise RuntimeError(f"Unsupported platform: {self.system} {self.machine}")

        self.set_executable_permissions(path)

        return path

    def get_platform_python_path(self):
        import pathlib

        return pathlib.Path("python", self.os_dir, self.arch_dir)

    def platform_path(self, posix_path: pathlib.Path):
        if self.system == "windows":
            import pathlib

            # Convert the PosixPath to a string
            path_str = str(posix_path)

            # Handle relative paths by checking if the path starts with '/'
            if path_str.startswith("/"):
                parts = path_str.lstrip("/").split("/", 1)
                if (
                    len(parts[0]) == 1 and parts[0].isalpha()
                ):  # Check if the first part is a single letter (drive letter)
                    drive_letter = parts[0].upper() + ":"
                    rest_of_path = parts[1] if len(parts) > 1 else ""
                else:
                    drive_letter = ""
                    rest_of_path = path_str
            else:
                drive_letter = ""
                rest_of_path = path_str

            # Replace forward slashes with backslashes
            windows_path_str = rest_of_path.replace("/", "\\")

            # Combine the drive letter and the rest of the path
            if drive_letter:
                windows_path = pathlib.Path(drive_letter + "\\" + windows_path_str)
            else:
                windows_path = pathlib.Path(windows_path_str)

            return windows_path
        return posix_path

    @staticmethod
    def stream_is_open(stream: typing.TextIO | typing.Any):
        import os

        try:
            os.fstat(stream.fileno())
            return True
        except (AttributeError, ValueError, OSError):
            return False

    @staticmethod
    def delete_existing_directories(base_dir: pathlib.Path):
        import pathlib
        import shutil

        for path in pathlib.Path(".").iterdir():
            if path.is_dir() and path.name.startswith(base_dir.stem):
                shutil.rmtree(path, ignore_errors=False)

    @staticmethod
    def create_unique_time_dir_name(base_dir: pathlib.Path) -> pathlib.Path:
        import datetime

        PlatformPythonManager.delete_existing_directories(base_dir)

        now = datetime.datetime.now()
        dir_name = now.strftime("%H%M%S")
        dir_path = base_dir.with_stem(f"{base_dir.stem}-{dir_name}")

        while dir_path.exists():
            now += datetime.timedelta(seconds=1)
            dir_name = now.strftime("%H%M%S")
            dir_path = base_dir.with_stem(f"{base_dir.stem}-{dir_name}")

        return dir_path

    def extract(
        self,
        directory: pathlib.Path,
        out_dir: str | None = None,
        stack: contextlib.ExitStack | None = None,
    ) -> tuple[pathlib.Path, pathlib.Path]:
        import os
        import pathlib
        import tempfile
        import zipfile

        directory_s = str(directory)

        # Ensure directory is within Zip
        with zipfile.ZipFile(sys.argv[0], "r") as zip_ref:
            if not any(member.startswith(directory_s) for member in zip_ref.namelist()):
                directory_s = directory.as_posix()
                if not any(
                    member.startswith(directory_s) for member in zip_ref.namelist()
                ):
                    raise FileNotFoundError(
                        f"File or directory not found in zip: {directory_s}"
                    )

        # optimistic option
        if not out_dir:
            # Make cosmopolitan-compatible temp path
            base_temp_dir_str = os.environ.get("TEMP")
            if not base_temp_dir_str:
                base_temp_dir = str(self.platform_path(pathlib.Path.cwd()))
            else:
                base_temp_dir = str(self.platform_path(pathlib.Path(base_temp_dir_str)))
            # Create a temporary directory and register
            temp_dir: pathlib.Path = pathlib.Path(tempfile.mkdtemp(dir=base_temp_dir))
        # compatible option
        else:
            temp_dir: pathlib.Path = pathlib.Path(out_dir)
            temp_dir.mkdir(exist_ok=True)

        if stack:
            import shutil

            stack.callback(lambda: (shutil.rmtree(temp_dir, ignore_errors=True)))

        # Extract directory from zip file that app was run from
        with zipfile.ZipFile(sys.argv[0], "r") as zip_ref:
            for member in zip_ref.namelist():
                if member.startswith(directory_s):
                    zip_ref.extract(member, temp_dir)

        # Return path to the extracted directory and temp_dir
        return temp_dir / directory_s, temp_dir


def main():
    import uuid

    platform_manager = PlatformPythonManager()
    run_uuid = uuid.uuid4().hex

    def run_entry():
        import AIServer

        AIServer.main()

    if "--run-uuid" in sys.argv:
        uuid_index = sys.argv.index("--run-uuid")
        sys.argv.pop(uuid_index)  # Remove the '--run-uuid' flag
        sys.argv.pop(uuid_index)  # Remove the actual UUID value

        import contextlib
        import pathlib

        with contextlib.ExitStack() as stack:
            lib_path_parts = [
                "platform-packages",
                platform_manager.os_dir,
                (
                    platform_manager.arch_dir
                    if platform_manager.system != "darwin"
                    else "universal2"
                ),
            ]
            unique_extract_dir_name = platform_manager.create_unique_time_dir_name(
                pathlib.Path("platform-packages")
            )
            lib_path, _ = platform_manager.extract(
                pathlib.Path(*lib_path_parts),
                stack=stack,
                out_dir=str(unique_extract_dir_name),
            )
            sys.path.insert(0, str(lib_path))

            run_entry()

    else:
        import contextlib
        import os
        import pathlib
        import subprocess

        with contextlib.ExitStack() as stack:
            platform_python_path = platform_manager.get_platform_python_path()
            unique_extract_dir_name = platform_manager.create_unique_time_dir_name(
                pathlib.Path("python")
            )
            platform_python, _ = platform_manager.extract(
                platform_python_path,
                stack=stack,
                out_dir=str(unique_extract_dir_name),
            )
            platform_python_bin = platform_manager.get_platform_python_bin(
                platform_python
            )

            new_args: list[str] = [
                str(platform_python_bin),
                *sys.argv,
                "--run-uuid",
                run_uuid,
            ]
            new_env: dict[str, str] = os.environ.copy()
            process: subprocess.Popen[bytes] | None = None

            try:
                process = subprocess.Popen(
                    new_args,
                    env=new_env,
                    stdin=(
                        sys.stdin
                        if platform_manager.stream_is_open(sys.stdin)
                        else None
                    ),
                    stdout=(
                        sys.stdout
                        if platform_manager.stream_is_open(sys.stdout)
                        else None
                    ),
                    stderr=(
                        sys.stderr
                        if platform_manager.stream_is_open(sys.stderr)
                        else None
                    ),
                    close_fds=False if platform_manager.system == "windows" else True,
                )

                process.wait()
                sys.exit(process.returncode)

            except KeyboardInterrupt:
                if process:
                    import signal

                    try:
                        process.send_signal(signal.SIGINT)
                        process.wait()
                        sys.exit(0)
                    except PermissionError:
                        pass
                    except Exception:
                        pass

                    sys.exit()


if __name__ == "__main__":
    main()
