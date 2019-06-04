from .namespace import ns_schema
res_schema = {
    "$schema": "http://json-schema.org/draft-07/schema/resource#",
    "$id": "tcsam.resource",
    "type": "object",
    "properties": {
        #"oneOf": [ns_schema]
    },
    "additionalProperties": {
        "type": "object",
        "oneOf": [ns_schema]
    }
}