# AIServer

### Build

Currently uses a pyz to run. It includes a custom `loader.py` to run platform-specific pythons and libraries. See the PEPs below for info.

https://peps.python.org/pep-0441/
https://peps.python.org/pep-0711/

You need [uv](https://docs.astral.sh/uv/) to build the project. It reads `.python-version` and installs Python 3.11 for you.

```sh
uv sync
```

The closest way to build this project would be something like this:

```sh
# stage the package and its runtime dependencies into build/
uv pip install --target build .
# byte-compile and drop the .py sources
uv run python -m compileall -b -q build
find build -name '*.py' -delete
# copy loader.py into directory as the zipapp entrypoint
cp loader.py build/__main__.py

# TRANSLATIONS
uv run python tools/compile_translations.py
uv run python tools/convert_translations.py

# PLATFORM DEPS
# create directory structure
mkdir -p build/platform-packages/darwin/universal2
mkdir -p build/platform-packages/linux/x86_64
# mkdir -p build/platform-packages/linux/aarch64
mkdir -p build/platform-packages/windows/x86_64
mkdir -p build/platform-packages/windows/x86
mkdir -p build/python/darwin/universal2
mkdir -p build/python/linux/x86_64
# mkdir -p build/python/linux/aarch64
mkdir -p build/python/windows/x86_64
mkdir -p build/python/windows/x86

# unzip wheels from vendor into platform dirs
# gotten from pypi
unzip -q vendor/grpcio-1.64.0-cp311-cp311-macosx_10_9_universal2.whl -d ./build/platform-packages/darwin/universal2/
unzip -q vendor/grpcio-1.64.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl -d ./build/platform-packages/linux/x86_64/
# unzip -q vendor/grpcio-1.64.0-cp311-cp311-manylinux_2_17_aarch64.whl -d ./build/platform-packages/linux/aarch64/
unzip -q vendor/grpcio-1.64.0-cp311-cp311-win_amd64.whl -d ./build/platform-packages/windows/x86_64/
unzip -q vendor/grpcio-1.64.0-cp311-cp311-win32.whl -d ./build/platform-packages/windows/x86/

# unzip pybi's from vendor into platform dirs
# gotten from https://pybi.vorpus.org/cpython-unofficial/
unzip -q vendor/cpython_unofficial-3.11.0-macosx_11_0_universal2.pybi -d ./build/python/darwin/universal2/
unzip -q vendor/cpython_unofficial-3.11.0-1-manylinux_2_17_x86_64.pybi -d ./build/python/linux/x86_64/
unzip -q vendor/cpython_unofficial-3.11.0-win_amd64.pybi -d ./build/python/windows/x86_64/
unzip -q vendor/cpython_unofficial-3.11.0-win32.pybi -d ./build/python/windows/x86/

# PACK
# zip the build directory into a pyz
cd build && zip ../AIServer.pyz -rq . && cd ..
```

### TRANSLATIONS

You need an OpenAI API key at the environment variable "OPENAI_API_KEY"

```sh
uv run pybabel extract -F babel.cfg -o locales/messages.pot .
uv run pybabel update -i locales/messages.pot -d locales
uv run python tools/openai_translate.py
uv run python tools/compile_translations.py
uv run python tools/convert_translations.py
```
