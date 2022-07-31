#!venv/bin/python
# -*- coding: utf-8 -*-

import sys
import serial


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
    # Get port & command
    port = sys.argv[1]
    command = ' '.join(sys.argv[2:])

    # If no command specified, show help
    if command == '':
        command = 'help'

    # Open flipper zero serial port
    f0 = serial.Serial(port, timeout=1)

    # Skip banner
    read_until_prompt(f0)

    # Send command
    f0.write(f"\n{command}\r\n".encode())

    # Skip command print
    f0.readline()

    # Print output
    print_until_prompt(f0)
