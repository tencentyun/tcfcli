from .function import func_schema
from .tcsam_macro import TcSamMacro as macro
ns_schema = {
    "$schema": "http://json-schema.org/draft-07/schema/resource/ns#",
    "$id": "tcsam.resource.ns", 
    "type": "object",
    "properties": {
        macro.Type: {
            "const": "TencentCloud::Serverless::Namespace"
        }
    },
    "required": [macro.Type],
    "additionalProperties": {
        "type": "object",
        "oneOf": [func_schema]
    }
}