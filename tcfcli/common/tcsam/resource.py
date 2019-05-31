from .namespace import ns_schema
res_schema = {
    "$schema": "http://json-schema.org/draft-07/schema/resource#",
    "$id": "tcsam.resource",
    "type": "object",
    "additionalProperties": ns_schema
}