# CLI for Flipper zero

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
```
