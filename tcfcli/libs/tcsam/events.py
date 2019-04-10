from tcfcli.libs.tcsam.model import *


class Timer(ProperModel):
    PROPER = {
        "CronExpression": {
            MUST: True,
            TYPE: mstr,
            VALUE: None
        },
        "Enable": {
            MUST: False,
            TYPE: mstr,
            VALUE: ["OPEN", "CLOSE"]
        }
    }

    def __init__(self, model, dft={}):
        super(Timer, self).__init__(model)

    def trigger_desc(self):
        return getattr(self, "CronExpression", None)


class COS(ProperModel):
    PROPER = {
        "Events": {
            MUST: True,
            TYPE: mstr,
            VALUE: None
        },
        "Filter": {
            MUST: False,
            TYPE: mmap,
            VALUE: None
        },
        "Enable": {
            MUST: False,
            TYPE: mstr,
            VALUE: ["OPEN", "CLOSE"]
        }
    }

    def __init__(self, model, dft={}):
        super(COS, self).__init__(model)

    def trigger_desc(self):
        return {"event": getattr(self, "Events"), "filter": getattr(self, "Filter", None)}


class APIGW(ProperModel):
    PROPER = {
        "StageName": {
            MUST: False,
            TYPE: mstr,
            VALUE: ["test", "prepub", "release"]
        },
        "HttpMethod": {
            MUST: False,
            TYPE: mstr,
            VALUE: ["ANY", "GET", "POST", "PUT", "DELETE", "HEAD"]
        }
    }

    def __init__(self, model, dft={}):
        super(APIGW, self).__init__(model)

    def trigger_desc(self):
        ret = {
            "api": {
                "authRequired": "FALSE",
                "requestConfig": {
                    "method": getattr(self, "HttpMethod", None)
                }
            },
            "service": {
                "serviceName": "SCF_API_SERVICE"
            },
            "release": {
                "environmentName": getattr(self, "StageName", None)
            }
        }
        return ret


class CMQ(ProperModel):
    PROPER = {
        "Enable": {
            MUST: False,
            TYPE: mstr,
            VALUE: ["OPEN", "CLOSE"]
        }
    }

    def __init__(self, model, dft={}):
        super(CMQ, self).__init__(model)

    def trigger_desc(self):
        return getattr(self, "Name", None)


class Events(TypeModel):
    AVA_TYPE = {
        "Timer": Timer,
        "COS": COS,
        "APIGW": APIGW,
        "CMQ": CMQ
    }

    def __init__(self, model, dft={}):
        super(Events, self).__init__(model, dft)

    def to_json(self):
        return self._serialize()