from .tcsam_macro import TcSamMacro as macro

glob_schema = {
    "$schema": "http://json-schema.org/draft-07/schema/global#",
    "$id": "tcsam.global",
    "type": "object",
    "properties": {
        macro.Function: {
            "type": "object",
            "properties": {
                macro.CodeUri: {"type": "string"},
                macro.Desc: {"type": "string"},
                macro.Envi: {
                    "type": "object",
                    "properties": {
                        macro.Vari: {
                            "type": "object",
                            "properties": {},
                            "additionalProperties": { "type": "string" }
                        }
                    },
                    "additionalProperties": False
                },
                macro.Handler: {"type": "string"},
                macro.MemSize: {"type": "integer", "exclusiveMinimum": 0},
                macro.Runtime: {
                    "type": "string",
                    "enum": ["Python2.7", "Python3.6", "Nodejs6.10", "Nodejs8.9",
                    "Php5", "Php7", "Go1", "Java8", "python2.7", "python3.6", 
                    "nodejs6.10", "nodejs8.9", "php5", "php7", "go1", "java8"]
                },
                macro.Timeout: {"type": "integer", "exclusiveMinimum": 0},
            },
            "additionalProperties": False
        }
    },
    "additionalProperties": False
}