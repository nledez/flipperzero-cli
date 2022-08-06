"""
Originally came from https://github.com/vstadnytskyi/mock_pyserial/blob/master/mock_pyserial/mock_serial.py
# fakeSerial.py
# D. Thiebaut
# A very crude simulator for PySerial assuming it
# is emulating an Arduino.
# Updated by Nicolas Ledez with some methods
"""
from logging import debug, info, warn, error


class Serial(object):
    def __init__(self, port='COM1', baudrate=115200, timeout=1,
                 bytesize=8, parity='N', stopbits=1, xonxoff=0,
                 rtscts=0):
        self.name     = port
        self.port     = port
        self.timeout  = timeout
        self.parity   = parity
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self.dsrdtr   = False
        self._isOpen     = True
        self._in_buffer  = b""
        self._out_buffer = b""
        self.communication_dictionary = {}

    def isOpen(self):
        return self._isOpen

    def open(self):
        self._isOpen = True

    def close(self):
        self._isOpen = False

    def write(self, string):
        debug("input buffer got value: {}".format(string))
        self._in_buffer += string

    def read(self, N=1):
        s = self._out_buffer[0:N]
        self._out_buffer = self._out_buffer[N:]
        debug("read: now self._data = ", self._out_buffer)
        return s

    def read_until(self, to_stop=b"\n"):
        offset = len(to_stop)
        try:
            returnIndex = self._out_buffer.index(to_stop)
            s = self._out_buffer[0:returnIndex+offset]
            self._out_buffer = self._out_buffer[returnIndex+offset:]
            return s
        except ValueError:
            string = self._out_buffer
            self._out_buffer = b""
            return string

    readline = read_until

    def in_waiting(self):
        raise NotImplementedError

    def out_waiting(self):
        raise NotImplementedError

    def __str__(self):
        return f"Serial<id=0xa81c10, open={self.isOpen()}>(port='{self.port}', baudrate={self.baudrate}, bytesize={self.bytesize}, parity='{self.parity}', stopbits={self.stopbits}, timeout={self.timeout}, xonxoff={self.xonxoff}, rtscts={self.rtscts}, dsrdtr={self.dsrdtr})"
