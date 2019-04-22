from tcfcli.libs.tcsam.model import Model
from tcfcli.libs.tcsam.model import VARIABLE
from tcfcli.common.user_exceptions import InvalidTemplateException


class Environment(Model):

    def __init__(self, model):
        if not isinstance(model, dict) or VARIABLE not in model \
         or not isinstance(model[VARIABLE], dict):
            raise InvalidTemplateException("invalid")

        for m in model[VARIABLE]:
            if not isinstance(model[VARIABLE][m], str):
                raise InvalidTemplateException("%s invalid" % m)
            try:
                setattr(self, m, model[VARIABLE][m])
            except InvalidTemplateException as e:
                raise InvalidTemplateException("{proper} ".format(proper=m) + str(e))

    def to_json(self):
        return {VARIABLE: self._serialize()}
