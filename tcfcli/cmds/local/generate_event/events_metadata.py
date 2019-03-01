EVENTS_METADATA = {
    "cmq": {
        "notification": {
            "filename": "notify",
            "help": "Generates an CMQ Topic notification event",
            "params": {
                "owner": {
                    "default": 12345678,
                }
            }
        }
    },
    "ckafka": {
        "consume": {
            "filename": "consume",
            "help": "Generates an ckafka consuming event",
            "params": {
            }
        }
    },
    "apigateway": {
        "proxy": {
            "filename": "proxy",
            "help": "Generates an API Gateway proxy event",
            "params": {
                "body": {
                    "default": "{\"msg\": \"hello apigateway\"}",
                }
            }
        }
    },
    "timer": {
        "timeup": {
            "filename": "timeout",
            "help": "Generates an Timer event",
            "params": {
                "message": {
                    "default": "hello timer",
                }
            }
        }
    },
    "cos": {
        "put": {
            "filename": "put",
            "help": "Generates an Cos Put event",
            "params": {
            }
        },
        "post": {
            "filename": "post",
            "help": "Generates an Cos Post event",
            "params": {
            }
        },
        "delete": {
            "filename": "delete",
            "help": "Generates an Cos Delete event",
            "params": {
            }
        }
    }
}
