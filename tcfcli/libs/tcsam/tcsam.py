from tcfcli.libs.tcsam.model import *
from tcfcli.libs.tcsam.events import *
from tcfcli.libs.tcsam.env import *
from tcfcli.libs.tcsam.vpc import *
from tcfcli.common.user_exceptions import InvalidTemplateException


class Function(ProperModel):
    PROPER = {
        "Handler": {
            MUST: True,
            TYPE: mstr,
            VALUE: None
        },
        "Runtime": {
            MUST: True,
            TYPE: mstr,
            VALUE: ("Python2.7", "Python3.6", "Nodejs6.10", "Nodejs8.9",
                    "PHP5", "PHP7", "Go1", "Java8")
        },
        "CodeUri": {
            MUST: False,
            TYPE: mstr,
            VALUE: None
        },
        "Description": {
            MUST: False,
            TYPE: mstr,
            VALUE: None
        },
        "MemorySize": {
            MUST: False,
            TYPE: mint,
            VALUE: None
        },
        "Timeout": {
            MUST: False,
            TYPE: mint,
            VALUE: False
        },
        "Environment": {
            MUST: False,
            TYPE: Environment,
            VALUE: None
        },
        "Events": {
            MUST: False,
            TYPE: Events,
            VALUE: None
        },
        "VpcConfig": {
            MUST: False,
            TYPE: VpcConfig,
            VALUE: None
        },
        "CosBucketName": {
            MUST: False,
            TYPE: mstr,
            VALUE: None
        },
        "CosObjectName": {
            MUST: False,
            TYPE: mstr,
            VALUE: None
        },
        "LocalZipFile": {
            MUST: False,
            TYPE: mstr,
            VALUE: None
        },
    }
    TYPE_PREFIX = "TencentCloud::Serverless::"

    def __init__(self, model, dft):
        if not isinstance(dft, dict):
            raise InvalidTemplateException("Globals invalid")
        if FUNCTION in dft:
            if not isinstance(dft[FUNCTION], dict):
                raise InvalidTemplateException("Globals invalid")
            for proper in dft[FUNCTION]:
                try:
                    setattr(self, proper, self.PROPER[proper][TYPE](dft[FUNCTION][proper]))
                except InvalidTemplateException as e:
                    raise InvalidTemplateException("{proper} ".format(proper=proper) + str(e))

        super(Function, self).__init__(model)


class Namespace(TypeModel):
    AVA_TYPE = {
        "TencentCloud::Serverless::Function": Function,
    }

    TYPE_PREFIX = "TencentCloud::Serverless::"

    def __init__(self, model, dft={}):
        super(Namespace, self).__init__(model, dft)


class Resources(TypeModel):
    AVA_TYPE = {
        "TencentCloud::Serverless::Namespace": Namespace,
    }

    def __init__(self, model):
        if not isinstance(model, dict):
            raise InvalidTemplateException("%s invalid" % self.__class__.__name__)
        resource = model.get("Resources", {})
        if not resource:
            raise InvalidTemplateException("Resources not found")
        glo = model.get("Globals", {})
        if not isinstance(resource, dict) or not isinstance(glo, dict):
            raise InvalidTemplateException("%s invalid" % self.__class__.__name__)

        super(Resources, self).__init__(resource, glo)

    def to_json(self):
        return {"Resources": self._serialize()}


if __name__ == '__main__':
    pass
