from .mock_serial import Serial


import pytest


def test_init():
    s0 = Serial()
    assert str(s0) == "Serial<id=0xa81c10, open=True>(port='COM1', baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1, xonxoff=0, rtscts=0, dsrdtr=False)"
    s1 = Serial('/dev/tty', 9600, 2, 7, 'Y', 0, 1, 1)
    assert str(s1) == "Serial<id=0xa81c10, open=True>(port='/dev/tty', baudrate=9600, bytesize=7, parity='Y', stopbits=0, timeout=2, xonxoff=1, rtscts=1, dsrdtr=False)"


def test_open():
    s0 = Serial()
    s0._isOpen = False
    s0.open()
    assert s0._isOpen is True


def test_close():
    s0 = Serial()
    s0._isOpen = True
    s0.close()
    assert s0._isOpen is False


def test_write():
    s0 = Serial()
    s0.write("Write a string in serial")
    assert s0._in_buffer == "Write a string in serial"
    s0.write("\nWith another line")
    assert s0._in_buffer == "Write a string in serial\nWith another line"


def test_read():
    s0 = Serial()
    s0._out_buffer = "A text waiting in output buffer\nWith many line\nStop."
    data = s0.read(24)
    assert data == "A text waiting in output"
    assert s0._out_buffer == " buffer\nWith many line\nStop."
    data = s0.read(7)
    assert data == " buffer"


def test_readline():
    s0 = Serial()
    s0._out_buffer = "line one\nline two\nline three"
    assert s0.readline() == "line one\n"
    assert s0.readline() == "line two\n"
    assert s0.readline() == "line three"
    assert s0.readline() == ""


def test_NotImplementedError():
    s0 = Serial()
    with pytest.raises(NotImplementedError):
        s0.in_waiting()
    with pytest.raises(NotImplementedError):
        s0.out_waiting()
