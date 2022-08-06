#!venv/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import serial
import hashlib
import argparse

from distutils.util import strtobool


CONFIG = {}


def load_config():
    parser = argparse.ArgumentParser(description="Flipper zero CLI")

    show_banner = os.environ.get("FLIPPER_ZERO_SHOW_BANNER", "False")
    port = os.environ.get("FLIPPER_ZERO_PORT")
    filename = os.environ.get("FLIPPER_ZERO_FILENAME")

    parser.add_argument("-p", "--port", default=port)
    parser.add_argument("-f", "--filename", default=filename)
    parser.add_argument("--show-config", action=argparse.BooleanOptionalAction,
                        default=False)
    parser.add_argument("--show-banner", action=argparse.BooleanOptionalAction,
                        default=strtobool(show_banner))

    (args, garbage) = parser.parse_known_args()

    CONFIG["show_config"] = args.show_config
    CONFIG["show_banner"] = args.show_banner
    CONFIG["port"] = args.port
    CONFIG["filename"] = args.filename

    return garbage


def show_config():
    print(f"show_banner: {CONFIG['show_banner']}")
    print(f"port: {CONFIG['port']}")


def read_until_prompt(f0):
    """
    Read serial until flipper zero prompt print
    """
    data = f0.read_until(b">: ")
    return data.decode()


def print_until_prompt(f0, show_prompt=False, offset=-5):
    """
    If show prompt remove latest chars with an offset
    """
    if show_prompt:
        offset = -0
    else:
        offset = offset

    # Print output
    print(read_until_prompt(f0)[:offset])


if __name__ == "__main__":
    command = " ".join(load_config())
    if CONFIG["show_config"]:
        show_config()
    if CONFIG["port"] is None:
        print("Please configure flipper zero serial port")
        sys.exit(1)

    # Get port & command
    print(f"Command: {command}")

    # If no command specified, show help
    if command == "":
        command = "help"

    # Open flipper zero serial port
    f0 = serial.Serial(CONFIG["port"], timeout=1)

    # Banner time
    if CONFIG["show_banner"]:
        print_until_prompt(f0)
    else:
        read_until_prompt(f0)

    # Send command
    f0.write(f"\n{command}\r".encode())

    # Skip command print
    f0.readline()

    if CONFIG["filename"]:
        if not os.path.exists(CONFIG["filename"]):
            print(f"{CONFIG['filename']} is missing.")
            sys.exit(1)
    # Print output
    if command[0:12] == "storage read" and CONFIG["filename"]:
        lines = read_until_prompt(f0).split("\n")
        print(f"Save to {CONFIG['filename']}")
        if lines[0][0:5] == "Size:":
            lines = lines[1:-3]
        else:
            lines = lines[:-3]
        with open(CONFIG["filename"], "w") as out:
            out.writelines("\n".join(lines))
            out.write("\n")
        print("\n".join(lines))
    if command[0:13] == "storage write" and CONFIG["filename"]:
        with open(CONFIG["filename"], "rb") as fs:
            f0.write(fs.read())
        f0.write(b"\x03")
        print_until_prompt(f0)
    if command[0:11] == "storage md5" and CONFIG["filename"]:
        with open(CONFIG["filename"], "rb") as fs:
            localhash = hashlib.md5(fs.read()).hexdigest()
        remotehash = f0.readline().decode().rstrip()
        read_until_prompt(f0)
        if localhash == remotehash:
            print(f"OK, same hash ({localhash})")
        else:
            print("KO different hashes:")
            print(f"local: '{localhash}'")
            print(f"remote: '{remotehash}'")
    else:
        print_until_prompt(f0)
    f0.close()
