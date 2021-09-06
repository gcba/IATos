import yaml
from pathlib import Path

config = Path("./config.yml")


def test_config_exists():
    assert config.exists()


def test_config_params():
    with open(config, "r") as file:
        params = yaml.load(file, Loader=yaml.FullLoader)

    assert "mel_spec" in params
    assert "color_spec" in params
