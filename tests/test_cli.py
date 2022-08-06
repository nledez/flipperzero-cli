from flipperzero_cli import CONFIG, load_config

DEFAULT_CONFIG = {"filename": None,
                  "port": None,
                  "show_banner": 0,
                  "show_config": False}
DEFAULT_COMMAND = ["help"]


def updated_config(data):
    new_config = DEFAULT_CONFIG.copy()
    for k, v in data.items():
        new_config[k] = v

    return new_config


def call_with(m, parameters=[], new_env={}):
    for k in [
        "FLIPPER_ZERO_SHOW_BANNER",
        "FLIPPER_ZERO_PORT",
        "FLIPPER_ZERO_FILENAME",
    ]:
        if k not in new_env:
            m.delenv(k, raising=False)
    for k, v in new_env.items():
        m.setenv(k, v)

    m.setattr("sys.argv", ["cli.py"] + parameters)


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

        call_with(m, [], {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        load_config()
        assert CONFIG == updated_config({"port": "/dev/flipper0"})

        call_with(m, [], {"FLIPPER_ZERO_FILENAME": "/home/flipper/dolpin.txt"})
        load_config()
        assert CONFIG == updated_config({"filename":
                                         "/home/flipper/dolpin.txt"})

        call_with(m, [], {
            "FLIPPER_ZERO_SHOW_BANNER": "1",
            "FLIPPER_ZERO_PORT": "/dev/flipper0",
            "FLIPPER_ZERO_FILENAME": "/home/flipper/dolpin.txt",
        })
        load_config()
        assert CONFIG == updated_config({
            "show_banner": True,
            "port": "/dev/flipper0",
            "filename": "/home/flipper/dolpin.txt",
        })

        # Test with command line parameters
        # -p --port
        call_with(m, ["-p", "/dev/flipper1"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"port": "/dev/flipper1"})

        call_with(m, ["--port", "/dev/flipper2"])
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"port": "/dev/flipper2"})

        call_with(m, ["--port", "/dev/flipper3"],
                  {"FLIPPER_ZERO_PORT": "/dev/flipper0"})
        assert load_config() == DEFAULT_COMMAND
        assert CONFIG == updated_config({"port": "/dev/flipper3"})

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

        call_with(m, ["--port", "/dev/flipper3"]+flipper_command)
        assert load_config() == flipper_command
        assert CONFIG == updated_config({"port": "/dev/flipper3"})

        call_with(m, flipper_command+["--port", "/dev/flipper3"])
        assert load_config() == flipper_command
        assert CONFIG == updated_config({"port": "/dev/flipper3"})
