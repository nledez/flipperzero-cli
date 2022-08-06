from flipperzero_cli import CONFIG, load_config

DEFAULT_CONFIG = {"filename": None,
                  "port": None,
                  "show_banner": 0,
                  "show_config": False}


def updated_config(data):
    new_config = DEFAULT_CONFIG.copy()
    for k, v in data.items():
        new_config[k] = v

    return new_config


def test_load_config(monkeypatch):
    assert CONFIG == {}

    # Test without env variable and command line parameters
    with monkeypatch.context() as m:
        m.delenv("FLIPPER_ZERO_SHOW_BANNER", raising=False)
        m.delenv("FLIPPER_ZERO_PORT", raising=False)
        m.delenv("FLIPPER_ZERO_FILENAME", raising=False)
        m.setattr("sys.argv", ["cli.py"])
        assert load_config() == []
        assert CONFIG == DEFAULT_CONFIG

    # Only test with env parameters
    with monkeypatch.context() as m:
        m.setenv("FLIPPER_ZERO_SHOW_BANNER", "1")
        m.delenv("FLIPPER_ZERO_PORT", raising=False)
        m.delenv("FLIPPER_ZERO_FILENAME", raising=False)
        load_config()
        assert CONFIG == updated_config({"show_banner": True})

    with monkeypatch.context() as m:
        m.delenv("FLIPPER_ZERO_SHOW_BANNER", raising=False)
        m.setenv("FLIPPER_ZERO_PORT", "/dev/flipper0")
        m.delenv("FLIPPER_ZERO_FILENAME", raising=False)
        load_config()
        assert CONFIG == updated_config({"port": "/dev/flipper0"})

    with monkeypatch.context() as m:
        m.delenv("FLIPPER_ZERO_SHOW_BANNER", raising=False)
        m.delenv("FLIPPER_ZERO_PORT", raising=False)
        m.setenv("FLIPPER_ZERO_FILENAME", "/home/flipper/dolpin.txt")
        load_config()
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin.txt"})

    with monkeypatch.context() as m:
        m.setenv("FLIPPER_ZERO_SHOW_BANNER", "1")
        m.setenv("FLIPPER_ZERO_PORT", "/dev/flipper0")
        m.setenv("FLIPPER_ZERO_FILENAME", "/home/flipper/dolpin.txt")
        load_config()
        assert CONFIG == updated_config({
            "show_banner": True,
            "port": "/dev/flipper0",
            "filename": "/home/flipper/dolpin.txt",
        })

    # Test with command line parameters
    with monkeypatch.context() as m:
        m.delenv("FLIPPER_ZERO_SHOW_BANNER", raising=False)
        m.delenv("FLIPPER_ZERO_PORT", raising=False)
        m.delenv("FLIPPER_ZERO_FILENAME", raising=False)

        # -p --port
        m.setattr("sys.argv", ["cli.py", "-p", "/dev/flipper1"])
        assert load_config() == []
        assert CONFIG == updated_config({"port": "/dev/flipper1"})

        m.setattr("sys.argv", ["cli.py", "--port", "/dev/flipper2"])
        assert load_config() == []
        assert CONFIG == updated_config({"port": "/dev/flipper2"})

        m.setenv("FLIPPER_ZERO_PORT", "/dev/flipper0")
        m.setattr("sys.argv", ["cli.py", "--port", "/dev/flipper3"])
        assert load_config() == []
        assert CONFIG == updated_config({"port": "/dev/flipper3"})
        m.delenv("FLIPPER_ZERO_PORT", raising=False)

        # -f --filename
        m.setattr("sys.argv", ["cli.py", "-f", "/home/flipper/dolpin1.txt"])
        assert load_config() == []
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin1.txt"})

        m.setattr("sys.argv", ["cli.py", "--filename",
                               "/home/flipper/dolpin2.txt"])
        assert load_config() == []
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin2.txt"})

        m.setenv("FLIPPER_ZERO_FILENAME", "/home/flipper/dolpin.txt")
        m.setattr("sys.argv", ["cli.py", "-f", "/home/flipper/dolpin3.txt"])
        assert load_config() == []
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin3.txt"})
        m.delenv("FLIPPER_ZERO_FILENAME", raising=False)

        # --show-banner
        m.setattr("sys.argv", ["cli.py", "--show-banner"])
        assert load_config() == []
        assert CONFIG == updated_config({"show_banner": True})

        m.setenv("FLIPPER_ZERO_SHOW_BANNER", "1")
        m.setattr("sys.argv", ["cli.py", "--show-banner"])
        assert load_config() == []
        assert CONFIG == updated_config({"show_banner": True})
        m.delenv("FLIPPER_ZERO_SHOW_BANNER", raising=False)

        # --show-config
        m.setattr("sys.argv", ["cli.py", "--show-config"])
        assert load_config() == []
        assert CONFIG == updated_config({"show_config": True})
