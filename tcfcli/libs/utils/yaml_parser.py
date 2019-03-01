import yaml
import json


def yaml_dump(dict_to_dump, file_path):
    with open(file_path, "w") as f:
        yaml.safe_dump(dict_to_dump, f, default_flow_style=False)


def yaml_parse(yaml_file):
    try:
        return json.loads(yaml_file)
    except ValueError:
        return yaml.safe_load(yaml_file)
