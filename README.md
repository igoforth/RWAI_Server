# AIServer

### Build

Currently uses a pyz to run. It includes a custom `loader.py` to run platform-specific pythons and libraries. See the PEP below for info.

https://peps.python.org/pep-0441/

Packaged pythons come from indygreg's amazing repo

https://github.com/indygreg/python-build-standalone/

You need python 3.11, pdm, and pdm-packer to build the project.

```sh
pip install pdm
pdm plugin add pdm-packer
```

The closest way to build this project would be something like this:

```sh
# install pdm-packer then run the below
pdm pack -m AIServer:main -c --pyc --no-py
# extract the resulting pyz to a folder
mkdir build
unzip AIServer.pyz -d build/
# copy loader.py into directory replacing __main__.py
cp loader.py build/__main__.py

# TRANSLATIONS
# Pack translations to build directory
python tools/compile_translations.py
python tools/convert_translations.py

# PATCHES
# I had to vendor the protobuf library because their current release hasn't released a commit that removes reliance on ctypes yet
cp vendor/protobuf/google/protobuf/internal/type_checkers.py build/google/protobuf/internal/type_checkers.py
# remove the .pyc if it exists to force the .py file to be used
rm build/google/protobuf/internal/type_checkers.pyc

# PLATFORM DEPS
# create directory structure
mkdir -p build/platform-packages/darwin/universal2
mkdir -p build/platform-packages/linux/x86_64
mkdir -p build/platform-packages/linux/aarch64
mkdir -p build/platform-packages/windows/x86_64
mkdir -p build/platform-packages/windows/x86
mkdir -p build/python/darwin/x86_64
mkdir -p build/python/darwin/arm64
mkdir -p build/python/linux/x86_64
mkdir -p build/python/linux/aarch64
mkdir -p build/python/windows/x86_64
mkdir -p build/python/windows/x86

# unzip wheels from vendor into platform dirs
# gotten from pypi
unzip vendor/grpcio-1.64.0-cp311-cp311-macosx_10_9_universal2.whl -d ./build/platform-packages/darwin/universal2/
unzip vendor/grpcio-1.64.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl -d ./build/platform-packages/linux/x86_64/
unzip vendor/grpcio-1.64.0-cp311-cp311-manylinux_2_17_aarch64.whl -d ./build/platform-packages/linux/aarch64/
unzip vendor/grpcio-1.64.0-cp311-cp311-win_amd64.whl -d ./build/platform-packages/windows/x86_64/
unzip vendor/grpcio-1.64.0-cp311-cp311-win32.whl -d ./build/platform-packages/windows/x86/

# unzip python builds from vendor into platform dirs
# gotten from https://github.com/indygreg/python-build-standalone/releases
# Darwin x86_64
tar -xvpf vendor/cpython-3.11.9+20240415-x86_64-apple-darwin-install_only.tar.gz -C ./build/python/darwin/x86_64/
mv ./build/python/darwin/x86_64/python/* ./build/python/darwin/x86_64/
rm -r ./build/python/darwin/x86_64/python/

# Darwin arm64
tar -xvpf vendor/cpython-3.11.9+20240415-aarch64-apple-darwin-install_only.tar.gz -C ./build/python/darwin/arm64/
mv ./build/python/darwin/arm64/python/* ./build/python/darwin/arm64/
rm -r ./build/python/darwin/arm64/python/

# Linux x86_64
tar -xvpf vendor/cpython-3.11.9+20240415-x86_64_v4-unknown-linux-musl-install_only.tar.gz -C ./build/python/linux/x86_64/
mv ./build/python/linux/x86_64/python/* ./build/python/linux/x86_64/
rm -r ./build/python/linux/x86_64/python/

# Linux aarch64
tar -xvpf vendor/cpython-3.11.9+20240415-aarch64-unknown-linux-gnu-install_only.tar.gz -C ./build/python/linux/aarch64/
mv ./build/python/linux/aarch64/python/* ./build/python/linux/aarch64/
rm -r ./build/python/linux/aarch64/python/

# Windows x86_64
tar -xvpf vendor/cpython-3.11.9+20240415-x86_64-pc-windows-msvc-install_only.tar.gz -C ./build/python/windows/x86_64/
mv ./build/python/windows/x86_64/python/* ./build/python/windows/x86_64/
rm -r ./build/python/windows/x86_64/python/

# Windows x86
tar -xvpf vendor/cpython-3.11.9+20240415-i686-pc-windows-msvc-install_only.tar.gz -C ./build/python/windows/x86/
mv ./build/python/windows/x86/python/* ./build/python/windows/x86/
rm -r ./build/python/windows/x86/python/

# zip the build directory into a pyz
cd build && zip ../AIServer.pyz -rq . && cd ..
```

### Translations

```sh
# You need an OpenAI API key at the environment variable "OPENAI_API_KEY"
pdm run pybabel extract -F babel.cfg -o locales/messages.pot .
pdm run pybabel update -i locales/messages.pot -d locales
python tools/openai_translate.py
python tools/compile_translations.py
python tools/convert_translations.py
```
