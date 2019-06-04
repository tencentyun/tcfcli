from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema import Draft7Validator
from .tcsam_schema import ts_schema
from .exception import TcSamException
from .tcsam_util import TcSamutil

Draft7Validator.check_schema(ts_schema)
def tcsam_validate(tcsam_data):
    try:
        TcSamutil.merge_globals(tcsam_data)
        validate(instance=tcsam_data, schema=ts_schema)
    except ValidationError as err:
        raise TcSamException("Validator the template file failed, {0}\n{1}".format(err.message, err.absolute_path))
    return tcsam_data