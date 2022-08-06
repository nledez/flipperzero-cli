"""
Originally came from https://github.com/vstadnytskyi/mock_pyserial/blob/master/mock_pyserial/mock_serial.py
# fakeSerial.py
# D. Thiebaut
# A very crude simulator for PySerial assuming it
# is emulating an Arduino.
# Updated by Nicolas Ledez with some methods
"""
from logging import debug, info, warn, error
# a Serial class emulator

# establishes responses to supported input commands
# as {'in command':'out command'}


class Serial(object):
    # init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
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
        self._in_buffer  = ""
        self._out_buffer = ""
        self.communication_dictionary = {}

    # isOpen()
    # returns True if the port to the Arduino is open.  False otherwise
    def isOpen(self):
        return self._isOpen

    # open()
    # opens the port
    def open(self):
        self._isOpen = True

    # close()
    # closes the port
    def close(self):
        self._isOpen = False

    # write()
    # writes a string of characters to the Arduino
    def write(self, string):
        """
        writes input string into input serial buffer

        Parameters
        ----------
        string:  (string)
            command as a string

        Returns
        -------

        Examples
        --------
        >>> ser.write('serial port command')
        """
        debug("input buffer got value: {}".format(string))
        self._in_buffer += string

    # read()
    # reads n characters from the fake Arduino. Actually n characters
    # are read from the string _data and returned to the caller.
    def read(self, N=1):
        s = self._out_buffer[0:N]
        self._out_buffer = self._out_buffer[N:]
        debug("read: now self._data = ", self._out_buffer)
        return s

    # readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline(self):
        try:
            returnIndex = self._out_buffer.index("\n")
            s = self._out_buffer[0:returnIndex+1]
            self._out_buffer = self._out_buffer[returnIndex+1:]
            return s
        except ValueError:
            string = self._out_buffer
            self._out_buffer = ""
            return string

    def in_waiting(self):
        raise NotImplementedError

    def out_waiting(self):
        raise NotImplementedError

    # __str__()
    # returns a string representation of the serial class
    def __str__(self):
        return f"Serial<id=0xa81c10, open={self.isOpen()}>(port='{self.port}', baudrate={self.baudrate}, bytesize={self.bytesize}, parity='{self.parity}', stopbits={self.stopbits}, timeout={self.timeout}, xonxoff={self.xonxoff}, rtscts={self.rtscts}, dsrdtr={self.dsrdtr})"
