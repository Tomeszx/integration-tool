import configparser
import json
import pathlib
from functools import lru_cache


def get_config(section, field=None):
    config = configparser.ConfigParser()
    file_path = pathlib.Path(__file__).parent.parent.absolute().joinpath(f"config/config.ini")
    config.read(file_path)
    if field:
        return config.get(section, field)
    return config.items(section)


@lru_cache
def get_podio_fields_ids(type: str):
    with open(f'config/podio_{type}_fields.json', 'r') as f:
        return json.load(f)


@lru_cache
def get_required_fields_per_task() -> dict:
    with open(f'config/tasks.json', 'r') as f:
        return json.load(f)
