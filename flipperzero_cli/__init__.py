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
    hide_command = os.environ.get("FLIPPER_ZERO_HIDE_COMMAND", "False")
    port = os.environ.get("FLIPPER_ZERO_PORT")
    filename = os.environ.get("FLIPPER_ZERO_FILENAME")

    parser.add_argument("-p", "--port", default=port)
    parser.add_argument("-f", "--filename", default=filename)
    parser.add_argument("--show-config", action="store_true",
                        default=False)
    parser.add_argument("--show-banner", action="store_true",
                        default=strtobool(show_banner))
    parser.add_argument("--hide-command", action="store_true",
                        default=strtobool(hide_command))

    (args, command) = parser.parse_known_args()

    CONFIG["show_config"] = args.show_config
    CONFIG["show_banner"] = args.show_banner
    CONFIG["hide_command"] = args.hide_command
    CONFIG["port"] = args.port
    CONFIG["filename"] = args.filename

    # If no command specified, show help
    if command == []:
        command = ["help"]

    return command


def show_config():
    print(f"show_banner: {CONFIG['show_banner']}")
    print(f"hide_command: {CONFIG['hide_command']}")
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
        print(read_until_prompt(f0))
    else:
        print(read_until_prompt(f0)[:offset])


def check_file_presence(filename):
    if not os.path.exists(filename):
        print(f"{filename} is missing.")
        sys.exit(1)
    return True


def flipper_init(s=serial.Serial):
    command = " ".join(load_config())
    if CONFIG["port"] is None:
        print("Please configure flipper zero serial port")
        sys.exit(1)

    # Open flipper zero serial port
    f0 = s(CONFIG["port"], timeout=1)

    return (command, f0)


def storage_read(f0):
    lines = read_until_prompt(f0).split("\n")
    if len(lines) == 1:
        print("Error in storage read")
        sys.exit(1)
    size = int(lines[0][6:])
    lines = lines[1:-3]

    return (size, "\n".join(lines)+"\n")


def save_file(content, filename, output=False):
    print(f"Save to {filename}")
    with open(filename, "w") as out:
        out.write(content)
    if output:
        print(content)


def download_from_flipper(f0, filename, output=True):
    (size, content) = storage_read(f0)
    save_file(content, filename, output)


def upload_to_flipper(f0, filename):
    # Check if filename exist
    check_file_presence(filename)
    with open(filename, "rb") as fs:
        f0.write(fs.read())
    f0.write(b"\x03")
    print_until_prompt(f0)


def check_local_md5(filename):
    with open(filename, "rb") as fs:
        return hashlib.md5(fs.read()).hexdigest()


def compare_md5(f0, filename):
    check_file_presence(filename)
    localhash = check_local_md5(filename)
    remotehash = f0.readline().decode().rstrip()
    read_until_prompt(f0)
    if localhash == remotehash:
        print(f"OK, same hash ({localhash})")
    else:
        print("KO different hashes:")
        print(f"local: '{localhash}'")
        print(f"remote: '{remotehash}'")


def main(s=serial.Serial):
    (command, f0) = flipper_init(s)
    if CONFIG["show_config"]:
        show_config()

    # Print command
    if not CONFIG["hide_command"]:
        print(f"Command: {command}")

    # Show banner. Or not.
    if CONFIG["show_banner"]:
        print_until_prompt(f0)
    else:
        read_until_prompt(f0)

    # Send command
    f0.write(f"\n{command}\r".encode())

    # Flush command print
    f0.readline()

    # Print output
    if command[0:12] == "storage read" and CONFIG["filename"]:
        download_from_flipper(f0, CONFIG["filename"])
    if command[0:13] == "storage write" and CONFIG["filename"]:
        upload_to_flipper(f0, CONFIG["filename"])
    if command[0:11] == "storage md5" and CONFIG["filename"]:
        compare_md5(f0, CONFIG["filename"])
    else:
        print_until_prompt(f0)
    f0.close()
