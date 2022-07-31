#!venv/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import serial
import argparse

from distutils.util import strtobool


CONFIG = {}


def load_config():
    parser = argparse.ArgumentParser(description='Flipper zero CLI')

    show_banner = os.environ.get('FLIPPER_ZERO_SHOW_BANNER', 'False')
    port = os.environ.get('FLIPPER_ZERO_PORT')

    parser.add_argument('-p', '--port', default=port)
    parser.add_argument('--show-config',
                        action=argparse.BooleanOptionalAction,
                        default=False)
    parser.add_argument('-b', '--show-banner',
                        action=argparse.BooleanOptionalAction,
                        default=show_banner)

    (args, garbage) = parser.parse_known_args()
    # print(args)
    # print(garbage)

    CONFIG["show_config"] = args.show_config
    CONFIG["show_banner"] = strtobool(args.show_banner)
    CONFIG["port"] = args.port

    return garbage


def show_config():
    print(f'show_banner: {CONFIG["show_banner"]}')
    print(f'port: {CONFIG["port"]}')


def read_until_prompt(f0):
    """
    Read serial until flipper zero prompt print
    """
    data = f0.read_until(b'>: ')
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


if __name__ == '__main__':
    command = ' '.join(load_config())
    if CONFIG["show_config"]:
        show_config()
    if CONFIG["port"] is None:
        print('Please configure flipper zero serial port')
        sys.exit(1)

    # Get port & command
    print(f'Command: {command}')

    # If no command specified, show help
    if command == '':
        command = 'help'

    # Open flipper zero serial port
    f0 = serial.Serial(CONFIG["port"], timeout=1)

    # Banner time
    if CONFIG["show_banner"]:
        print_until_prompt(f0)
    else:
        read_until_prompt(f0)

    # Send command
    f0.write(f"\n{command}\r\n".encode())

    # Skip command print
    f0.readline()

    # Print output
    print_until_prompt(f0)
