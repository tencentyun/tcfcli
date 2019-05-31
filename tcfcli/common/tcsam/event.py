from .tcsam_macro import TcSamMacro as macro
apigw_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "tcsam.ns.func.event.apigw",
    "type": "object",
    "properties": {
        macro.Type: {"const": "APIGW"},
        macro.Properties: {
            "type": "object",
            "properties": {
                "StageName": {
                    "type": "string",
                    "enum": ["test", "prepub", "release"]
                },
                "HttpMethod": {
                    "type": "string",
                    "enum": ["ANY", "GET", "POST", "PUT", "DELETE", "HEAD"]
                },
                "IntegratedResponse": {
                    "type": "boolean",
                }
            },
            "additionalProperties": False
        }
    },
    "required": [macro.Type, macro.Properties],
    "additionalProperties": False
}



timer_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "tcsam.ns.func.event.timer",
    "type": "object",
    "properties": {
        macro.Type: {"const": "Timer"},
        macro.Properties: {
            "type": "object",
            "properties": {
                "CronExpression": {"type": "string"},
                "Enable": {
                    "enum": ["OPEN", "CLOSE", True, False]
                }   
            },
            "required": ["CronExpression"],
            "additionalProperties": False
        },
    },
    "required": [macro.Type, macro.Properties],
    "additionalProperties": False,
}


cmq_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "tcsam.ns.func.event.cmq",
    "type": "object",
    "properties": {
        macro.Type: {"const": "CMQ"},
        macro.Properties: {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    "required": [macro.Type, macro.Properties],
    "additionalProperties": False
}


cos_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "tcsam.ns.func.event.cos",
    "type": "object",
    "properties": {
        macro.Type: {"const": "COS"},
        macro.Properties: {
            "type": "object",
            "properties": {
                "Filter": {
                    "type": "object",
                    "properties": {
                        "Prefix": {"type": "string"},
                        "Suffix": {"type": "string"}
                    }
                },
                "Bucket": {"type": "string"},
                "Events": {"type": "string"},
                "Enable": {
                    "enum": ["OPEN", "CLOSE", True, False]
                }
            },
            "required": ["Events"],
            "additionalProperties": False
        }
    },
    "required": [macro.Type, macro.Properties],
    "additionalProperties": False
}