from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema import Draft7Validator
from .tcsam_schema import ts_schema

Draft7Validator.check_schema(ts_schema)
def tcsam_validate(tcsam_data):
    try:
        validate(instance=tcsam_data, schema=ts_schema)
    except ValidationError as err:
        return str(err).split("\n")[0]