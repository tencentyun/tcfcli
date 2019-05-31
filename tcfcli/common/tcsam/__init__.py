from jsonschema import validate
from .tcsam_schema import ts_schema


def tcsam_validate(tcsam_data):
    validate(instance=tcsam_data, schema=ts_schema)