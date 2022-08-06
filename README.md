# CLI for Flipper zero

[![Tests on push](https://github.com/nledez/flipperzero-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/nledez/flipperzero-cli/actions/workflows/tests.yml) [![Coverage Status](https://coveralls.io/repos/github/nledez/flipperzero-cli/badge.svg)](https://coveralls.io/github/nledez/flipperzero-cli)

Inspirated from:

https://github.com/lomalkin/flipperzero-cli-tools

And

https://github.com/flipperdevices/flipperzero_protobuf_py


## Install

```
# For linux users
sudo apt install python3 python3-venv python3-pip

# For everyone
git clone https://github.com/nledez/flipperzero-cli
cd flipper-cli-tools
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

## Usage

```
# to activate python virtual environment
. venv/bin/activate
# to deactivate
deactivate
```

## Install for test

```
pip install -r requirements.txt -r requirements_test.txt
pytest
```

### Tools

```
# Exec `help` command
python cli.py --show-banner --port=/dev/tty<path to Flipper serial> help

# Same with other commands
python cli.py --port=/dev/tty<path to Flipper serial> storage info /ext

# Define parameter as environement varaible
export FLIPPER_ZERO_SHOW_BANNER=1
export FLIPPER_ZERO_PORT=/dev/tty<path to Flipper serial>

python cli.py help
python cli.py storage info /ext
python cli.py --filename=demo_windows.txt storage read /ext/badusb/demo_windows.txt
python cli.py --filename=demo_linux.txt storage write /ext/badusb/demo_linux.txt
python cli.py --filename=demo_macos.txt storage md5 /ext/badusb/demo_macos.txt
```
