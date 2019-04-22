from tcfcli.common.user_exceptions import InvalidTemplateException
MUST = "must"
VALUE = "value"
DEFAULT = "default"
TYPE = "Type"
PROPERTY = "Properties"
VARIABLE = "Variables"
RESOURCE = "Resources"
FUNCTION = "Function"
GLOBAL = "Globals"
mint = lambda x: int(x)
mstr = lambda x: str(x)
mbool = lambda x: bool(x)
mmap = lambda x: x


class Model(object):

    TYPE_PREFIX = ""

    def _serialize(self):
        """Get all params which are not None if None is not allowed."""
        js = {}
        propers = vars(self)

        for k, v in propers.items():
            if isinstance(v, Model):
                js[k] = v.to_json()
            else:
                js[k] = v
        return js

    def to_json(self):
        return self._serialize()


class ProperModel(Model):
    PROPER = {
    }

    def __init__(self, model):
        if not isinstance(model, dict) or PROPERTY not in model:
            raise InvalidTemplateException("%s invalid" % PROPERTY)
        if not isinstance(model[PROPERTY], dict):
            if model[PROPERTY] is None:
                model[PROPERTY] = {}
            else:
                raise InvalidTemplateException("%s invalid" % PROPERTY)

        for m in model[PROPERTY]:
            if m not in self.PROPER:
                raise InvalidTemplateException("%s invalid" % m)
            try:
                setattr(self, m, self.PROPER[m][TYPE](model[PROPERTY][m]))
            except InvalidTemplateException as e:
                raise InvalidTemplateException("{proper} ".format(proper=m) + str(e))

        proper = [x for x in self.PROPER if self.PROPER[x][MUST]]
        for p in proper:
            v = getattr(self, p, None)
            if v is None:
                raise InvalidTemplateException("%s invalid" % p)
            elif isinstance(self.PROPER[p][VALUE], tuple) and v not in self.PROPER[p][VALUE]:
                raise InvalidTemplateException("%s invalid" % p)

    def to_json(self):
        return {TYPE: self.TYPE_PREFIX + self.__class__.__name__, PROPERTY: self._serialize()}


class TypeModel(Model):
    AVA_TYPE = {
    }

    def __init__(self, model, dft={}):
        if not isinstance(model, dict):
            raise InvalidTemplateException("invalid")
        for m in model:
            mod = model[m]
            if not isinstance(mod, dict) or TYPE not in mod:
                raise InvalidTemplateException("%s invalid" % m)
            type = mod[TYPE]
            del mod[TYPE]
            if type not in self.AVA_TYPE:
                raise InvalidTemplateException("%s invalid" % m)
            try:
                setattr(self, m, self.AVA_TYPE[type](mod, dft))
            except InvalidTemplateException as e:
                raise InvalidTemplateException("{proper} ".format(proper=m) + str(e))

    def to_json(self):
        t = self._serialize()
        t[TYPE] = self.TYPE_PREFIX + self.__class__.__name__
        return t