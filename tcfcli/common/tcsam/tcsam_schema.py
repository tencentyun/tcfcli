from .resource import res_schema
from .glob import glob_schema
from .tcsam_macro import TcSamMacro as macro
ts_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "tcsam",
    "type": "object",
    "properties": {
        macro.Resources: res_schema,
        macro.Globals: glob_schema
    },
    "required": [macro.Resources],
    "additionalProperties": False
}