# AIServer

### Build

Currently uses a pyz to run. It includes a custom `loader.py` to run platform-specific pythons and libraries. See the PEPs below for info.

https://peps.python.org/pep-0441/
https://peps.python.org/pep-0711/

The closest way to build this project would be something like this:

```sh
# install pdm-packer then run the below
pdm pack -m AIServer:main -c --pyc --no-py
# extract the resulting pyz to a folder
mkdir build
unzip AIServer.pyz build/
# copy loader.py into directory replacing __main__.py
cp loader.py build/__main__.py

# PATCHES
# I had to vendor the protobuf library because their current release hasn't released a commit that removes reliance on ctypes yet
cp vendor/protobuf/google/protobuf/internal/type_checkers.py build/google/protobuf/internal/type_checkers.py
# remove the .pyc if it exists to force the .py file to be used
rm build/google/protobuf/internal/type_checkers.pyc

# PLATFORM DEPS
# create directory structure
mkdir -p build/platform-packages/darwin/universal2
mkdir -p build/platform-packages/linux/x86_64
mkdir -p build/platform-packages/windows/x86
mkdir -p build/platform-packages/windows/x86_64
mkdir -p build/python/darwin/universal2
mkdir -p build/python/linux/x86_64
mkdir -p build/python/windows/x86
mkdir -p build/python/windows/x86_64
# unzip wheels from vendor into platform dirs
# gotten from pypi
unzip vendor/grpcio-1.64.0-cp311-cp311-macosx_10_9_universal2.whl ./build/platform-packages/darwin/universal2/
unzip vendor/grpcio-1.64.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl ./build/platform-packages/darwin/universal2/
unzip vendor/grpcio-1.64.0-cp311-cp311-win32.whl ./build/platform-packages/windows/x86/
unzip vendor/grpcio-1.64.0-cp311-cp311-win_amd64.whl ./build/platform-packages/windows/x86_64/
# unzip pybi's from vendor into platform dirs
# gotten from https://pybi.vorpus.org/cpython-unofficial/
unzip vendor/cpython_unofficial-3.11.0-macosx_11_0_universal2.pybi ./build/python/darwin/universal2/
unzip vendor/cpython_unofficial-3.11.0-1-manylinux_2_17_x86_64.pybi ./build/python/linux/x86_64/
unzip vendor/cpython_unofficial-3.11.0-win32.pybi ./build/python/windows/x86/
unzip vendor/cpython_unofficial-3.11.0-win_amd64.pybi ./build/python/windows/x86_64/

# TRANSLATIONS
# You need an OpenAI API key at the environment variable "OPENAI_API_KEY"
pdm run pybabel extract -F babel.cfg -o locales/messages.pot .
pdm run pybabel update -i locales/messages.pot -d locales
python tools/translate.py
python tools/compile_translations.py

# PACK
# zip the build directory into a pyz
cd build && zip ../AIServer.pyz -rq . && cd ..
```
