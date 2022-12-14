from flipperzero_cli import CONFIG, load_config, show_config, \
    read_until_prompt, print_until_prompt, check_file_presence, \
    flipper_init, main, \
    storage_read, save_file, download_from_flipper, \
    upload_to_flipper, check_local_md5, compare_md5

import builtins
import pytest

from unittest.mock import patch, mock_open
from .mock_serial import Serial

DEFAULT_CONFIG = {"filename": None,
                  "port": None,
                  "show_banner": 0,
                  "hide_command": False,
                  "show_config": False}
DEFAULT_COMMAND = ["help"]


# Helpers
def updated_config(data):
    new_config = DEFAULT_CONFIG.copy()
    for k, v in data.items():
        new_config[k] = v

    return new_config


def call_with(m, parameters=[], new_env={}):
    for k in [
        "FLIPPER_ZERO_SHOW_BANNER",
        "FLIPPER_ZERO_HIDE_COMMAND",
        "FLIPPER_ZERO_PORT",
        "FLIPPER_ZERO_FILENAME",
    ]:
        if k not in new_env:
            m.delenv(k, raising=False)
    for k, v in new_env.items():
        m.setenv(k, v)

    m.setattr("sys.argv", ["cli.py"] + parameters)


# Tests
def test_load_config(monkeypatch):
    with monkeypatch.context() as m:
        # Test without env variable and command line parameters
        call_with(m, [])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == DEFAULT_CONFIG

        # Only test with env parameters
        call_with(m, [], {"FLIPPER_ZERO_SHOW_BANNER": "1"})
        load_config()
        assert CONFIG == updated_config({"show_banner": True})

        call_with(m, [], {"FLIPPER_ZERO_HIDE_COMMAND": "1"})
        load_config()
        assert CONFIG == updated_config({"hide_command": True})

        call_with(m, [], {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        load_config()
        assert CONFIG == updated_config({"port": "/dev/flipper0"})

        call_with(m, [], {"FLIPPER_ZERO_FILENAME": "/home/flipper/dolpin.txt"})
        load_config()
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin.txt"})

        call_with(m, [], {
            "FLIPPER_ZERO_SHOW_BANNER": "1",
            "FLIPPER_ZERO_HIDE_COMMAND": "0",
            "FLIPPER_ZERO_PORT": "/dev/flipper0",
            "FLIPPER_ZERO_FILENAME": "/home/flipper/dolpin.txt",
        })
        load_config()
        assert CONFIG == updated_config({
            "show_banner": True,
            "hide_command": False,
            "port": "/dev/flipper0",
            "filename": "/home/flipper/dolpin.txt",
        })

        # Test with command line parameters
        # -p --port
        call_with(m, ["-p", "/dev/flipper0"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"port": "/dev/flipper0"})

        call_with(m, ["--port", "/dev/flipper0"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"port": "/dev/flipper0"})

        call_with(m, ["--port", "/dev/flipper1"],
                  {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"port": "/dev/flipper1"})

        # -f --filename
        call_with(m, ["-f", "/home/flipper/dolpin1.txt"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin1.txt"})

        call_with(m, [ "--filename", "/home/flipper/dolpin2.txt"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin2.txt"})

        call_with(m, ["-f", "/home/flipper/dolpin3.txt"],
                  {"FLIPPER_ZERO_FILENAME": "/home/flipper/dolpin.txt"})
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin3.txt"})

        # --show-banner
        call_with(m, ["--show-banner"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"show_banner": True})

        call_with(m, ["--show-banner"], {"FLIPPER_ZERO_SHOW_BANNER": "1"})
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"show_banner": True})

        # --hide-command
        call_with(m, ["--hide-command"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"hide_command": True})

        call_with(m, ["--hide-command"], {"FLIPPER_ZERO_HIDE_COMMAND": "1"})
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"hide_command": True})

        # --show-config
        call_with(m, ["--show-config"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"show_config": True})

        # Test different values for FLIPPER_ZERO_SHOW_BANNER
        for v in ["1", "true", "True"]:
            call_with(m, [], {"FLIPPER_ZERO_SHOW_BANNER": v})
            assert load_config() == DEFAULT_COMMAND
            assert CONFIG == updated_config({"show_banner": True})
        for v in ["false", "False"]:
            call_with(m, [], {"FLIPPER_ZERO_SHOW_BANNER": v})
            assert load_config() == DEFAULT_COMMAND
            assert CONFIG == updated_config({"show_banner": False})

        # Test if argparse leave "garbage" in parsing
        flipper_command = ["storage", "info", "/ext"]
        call_with(m, flipper_command)
        assert load_config() == flipper_command
        assert CONFIG == DEFAULT_CONFIG

        call_with(m, ["--port", "/dev/flipper0"]+flipper_command)
        assert load_config() == flipper_command
        assert CONFIG == updated_config({"port": "/dev/flipper0"})

        call_with(m, flipper_command+["--port", "/dev/flipper0"])
        assert load_config() == flipper_command
        assert CONFIG == updated_config({"port": "/dev/flipper0"})


def test_show_config(monkeypatch, capsys):
    with monkeypatch.context() as m:
        call_with(m, ["--port", "/dev/flipper0"])
        load_config()
        show_config()
        captured = capsys.readouterr()
        assert captured.out == "show_banner: 0\nhide_command: 0\nport: /dev/flipper0\n"

        call_with(m, ["--port", "/dev/flipper1", "--hide-command"])
        load_config()
        show_config()
        captured = capsys.readouterr()
        assert captured.out == "show_banner: 0\nhide_command: True\nport: /dev/flipper1\n"

        call_with(m, ["--show-banner", "--port", "/dev/flipper1"])
        load_config()
        show_config()
        captured = capsys.readouterr()
        assert captured.out == "show_banner: True\nhide_command: 0\nport: /dev/flipper1\n"


def test_read_until_prompt():
    f0 = Serial()
    simple_prompt = b"Text before\nFlipper prompt\n>: "
    f0._out_buffer = simple_prompt
    assert read_until_prompt(f0) == simple_prompt.decode()


FLIPPER_SD_INFO_PRINT = """Label: FLIPPER SD
Type: FAT32
3886080KB total
3841024KB free
"""
FLIPPER_SD_INFO = FLIPPER_SD_INFO_PRINT.encode() + b"""
>: ."""


def test_print_until_prompt(capsys):
    f0 = Serial()
    simple_prompt = b"Text before\nFlipper prompt\n>: "
    f0._out_buffer = simple_prompt
    print_until_prompt(f0, show_prompt=True)
    captured = capsys.readouterr()
    assert captured.out == simple_prompt.decode()+"\n"

    f0._out_buffer = FLIPPER_SD_INFO
    print_until_prompt(f0, show_prompt=True)
    captured = capsys.readouterr()
    assert captured.out == FLIPPER_SD_INFO.decode()[:-1]+"\n"

    f0._out_buffer = FLIPPER_SD_INFO
    print_until_prompt(f0, show_prompt=False)
    captured = capsys.readouterr()
    assert captured.out == FLIPPER_SD_INFO_PRINT


@patch("os.path.exists")
def test_check_file_presence(patch_exists):
    # Test missing file
    patch_exists.return_value = False
    with pytest.raises(SystemExit) as e:
        check_file_presence("/tmp/missing_file")
    assert e.type == SystemExit
    assert e.value.code == 1

    # Test existing file
    patch_exists.return_value = True
    assert check_file_presence("/tmp/existing_file") == True


def test_flipper_init(monkeypatch, capsys):
    with pytest.raises(SystemExit) as e:
        (command, f0) = flipper_init()
    assert e.type == SystemExit
    assert e.value.code == 1

    captured = capsys.readouterr()
    assert captured.out == "Please configure flipper zero serial port\n"

    with monkeypatch.context() as m:
        call_with(m, [], {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        (command, f0) = flipper_init(s=Serial)
    assert command == "help"


STORAGE_READ_01_HEADER = b"""Size: 164
"""
STORAGE_READ_01_CONTENT = b"""In faucibus dignissim ullamcorper.
Nulla quis molestie lacus.
Pellentesque congue dui et felis pharetra eleifend.
Integer magna eros. efficitur sed porta sit amet.
"""
STORAGE_READ_01_FOOTER = b"""

>: ."""

STORAGE_READ_01_RAW = STORAGE_READ_01_HEADER + \
    STORAGE_READ_01_CONTENT + \
    STORAGE_READ_01_FOOTER


def test_storage_read():
    f0 = Serial()
    f0._out_buffer = STORAGE_READ_01_RAW
    (size, data) = storage_read(f0)
    assert size == 164
    assert data == STORAGE_READ_01_CONTENT.decode()


def test_save_file(capsys):
    mock_write = mock_open()
    with patch.object(builtins, "open", mock_write, create=True) as patched_open:
        save_file(STORAGE_READ_01_CONTENT.decode(),
                "/tmp/file_2_save.txt",
                output=False)
        captured = capsys.readouterr()
        assert captured.out == "Save to /tmp/file_2_save.txt\n"
        assert patched_open.mock_calls[2][1][0] == STORAGE_READ_01_CONTENT.decode()

        save_file(STORAGE_READ_01_CONTENT.decode(),
                "/tmp/file_2_save.txt",
                output=True)
        captured = capsys.readouterr()
        assert captured.out == "Save to /tmp/file_2_save.txt\n" + \
            STORAGE_READ_01_CONTENT.decode() + "\n"


def test_download_from_flipper(capsys):
    f0 = Serial()
    f0._out_buffer = STORAGE_READ_01_RAW
    mock_write = mock_open()
    with patch.object(builtins, "open", mock_write, create=True) as patched_open:
        download_from_flipper(f0, "/tmp/file_2_save.txt", output=False)
    captured = capsys.readouterr()
    assert captured.out == "Save to /tmp/file_2_save.txt\n"

STORAGE_WRITE_01_HEADER = b"Just write your text data. New line by Ctrl+Enter, exit by Ctrl+C.\n\n"
STORAGE_WRITE_01_FOOTER = b"""
>: """
STORAGE_WRITE_01_OUT = STORAGE_WRITE_01_HEADER + \
    STORAGE_READ_01_CONTENT
STORAGE_WRITE_01_RAW = STORAGE_WRITE_01_OUT + \
    STORAGE_WRITE_01_FOOTER

@patch("os.path.exists")
def test_upload_to_flipper(patch_exists, capsys):
    f0 = Serial()
    f0._out_buffer = STORAGE_WRITE_01_RAW
    patch_exists.return_value = True
    with patch("builtins.open", mock_open(read_data=STORAGE_READ_01_CONTENT)) as mock_file:
        upload_to_flipper(f0, "/tmp/file_2_upload.txt")
    mock_file.assert_called_with("/tmp/file_2_upload.txt", "rb")
    captured = capsys.readouterr()
    assert captured.out == STORAGE_WRITE_01_OUT.decode()


def test_check_local_md5():
    with patch("builtins.open", mock_open(read_data=STORAGE_READ_01_CONTENT)) as mock_file:
        localhash = check_local_md5("/tmp/local_filename.txt")
    mock_file.assert_called_with("/tmp/local_filename.txt", "rb")
    assert localhash == "9cb4a477cbbf515f7dffb459f1e05594"


GOD_HASH = "9cb4a477cbbf515f7dffb459f1e05594"
BAD_HASH = "a7b073ead2a733491a4a407e777b2e59"
@patch("os.path.exists")
@patch("flipperzero_cli.check_local_md5")
def test_compare_md5(patch_check_local_md5, patch_exists, capsys):
    f0 = Serial()
    f0._out_buffer = f"{GOD_HASH}\n\n>: ".encode()
    patch_exists.return_value = True
    patch_check_local_md5.return_value = GOD_HASH
    compare_md5(f0, "/tmp/local_filename.txt")
    captured = capsys.readouterr()
    assert captured.out == f"OK, same hash ({GOD_HASH})\n"

    f0 = Serial()
    f0._out_buffer = f"{GOD_HASH}\n\n>: ".encode()
    patch_exists.return_value = True
    patch_check_local_md5.return_value = BAD_HASH
    compare_md5(f0, "/tmp/local_filename.txt")
    captured = capsys.readouterr()
    assert captured.out == f"""KO different hashes:
local: '{BAD_HASH}'
remote: '{GOD_HASH}'
"""


def test_main(monkeypatch, capsys):
    with pytest.raises(SystemExit) as e:
        main()
    assert e.type == SystemExit
    assert e.value.code == 1

    captured = capsys.readouterr()
    assert captured.out == "Please configure flipper zero serial port\n"

    with monkeypatch.context() as m:
        call_with(m, [], {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        main(s=Serial)
        captured = capsys.readouterr()
        assert captured.out == "Command: help\n\n"

    with monkeypatch.context() as m:
        call_with(m, ["--show-config"], {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        main(s=Serial)
        captured = capsys.readouterr()
        assert captured.out == """show_banner: 0
hide_command: 0
port: /dev/flipper0
Command: help

"""

    with monkeypatch.context() as m:
        call_with(m, ["--show-banner"], {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        main(s=Serial)
        captured = capsys.readouterr()
        assert captured.out == "Command: help\n\n\n"

    with monkeypatch.context() as m:
        mock_write = mock_open()
        with patch.object(builtins, "open", mock_write, create=True) as patched_open:
            call_with(m, ["--filename=/tmp/to_save.txt",
                          "storage", "read", "/ext/badusb/demo_macos.txt"],
                      {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
            with pytest.raises(SystemExit) as e:
                main(s=Serial)
            assert e.type == SystemExit
            assert e.value.code == 1
            captured = capsys.readouterr()
            assert captured.out == "Command: storage read /ext/badusb/demo_macos.txt\nError in storage read\n"

        call_with(m, ["--filename=/tmp/to_write.txt",
                        "storage", "write", "/ext/badusb/demo_macos.txt"],
                    {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        with pytest.raises(SystemExit) as e:
            main(s=Serial)
        assert e.type == SystemExit
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert captured.out == "Command: storage write /ext/badusb/demo_macos.txt\n/tmp/to_write.txt is missing.\n"

    with monkeypatch.context() as m:
        call_with(m, [
            "--filename=/tmp/to_md5.txt", "storage", "md5",
            "/ext/badusb/demo_macos.txt"],
            {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        with pytest.raises(SystemExit) as e:
            main(s=Serial)
        captured = capsys.readouterr()
        assert captured.out == \
            """Command: storage md5 /ext/badusb/demo_macos.txt
/tmp/to_md5.txt is missing.
"""
