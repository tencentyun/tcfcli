from tcfcli.libs.tcsam.model import *


class VpcConfig(ProperModel):
    PROPER = {
        "VpcId": {
            MUST: True,
            TYPE: mstr,
            VALUE: None
        },
        "SubnetId": {
            MUST: True,
            TYPE: mstr,
            VALUE: None
        },

    }

    TYPE_PREFIX = "TencentCloud::Serverless::"

    def __init__(self, model):
        super(VpcConfig, self).__init__(model)

    def to_json(self):
        return self._serialize()
