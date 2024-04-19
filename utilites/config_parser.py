import configparser
import pathlib


def get_config(section, field=None):
    config = configparser.ConfigParser()
    file_path = pathlib.Path(__file__).parent.parent.absolute().joinpath(f"config/config.ini")
    config.read(file_path)
    if field:
        return config.get(section, field)
    return config.items(section)
