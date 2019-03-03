import os
import click
import platform

sysstr = platform.system()
if (sysstr == 'Linux' or 'Darwin'):
    home = os.path.expanduser('~')
    _USER_CONFIG_FILE = home + '/.tcli_config.ini'
else:
    _USER_CONFIG_FILE = ".tcli_config.ini"

version = platform.python_version()
if version >= '3':
    from configparser import ConfigParser
else:
    from ConfigParser import ConfigParser


class CliConfigParser(ConfigParser):

    def __init__(self, defaults=None):
        ConfigParser.__init__(self,defaults=None)
        #super(CliConfigParser, self).__init__(defaults)

    def optionxform(self, optionstr):
        return optionstr


class UserConfig(object):

    API = "API"

    def __init__(self):
        self.secret_id = 'None'
        self.secret_key = 'None'
        self.region = 'None'
        self.appid = 'None'
        self._load_config()

    def set_attrs(self, attrs):
        for k in attrs:
            if hasattr(self, self._name_attr2obj(k)) and attrs[k]:
                setattr(self, self._name_attr2obj(k), attrs[k])

    def get_attrs(self, attrs):
        objs = self._list_attrs()
        ret = {}
        for attr in [ k for k, v in attrs.items() if v]:
            obj = self._name_attr2obj(attr)
            if obj in objs:
                ret[self._name_obj2attr(attr)] = objs[obj]
        return ret

    def flush(self):
        self._dump_config()

    def _load_config(self):
        cf = CliConfigParser()
        if not cf.read(_USER_CONFIG_FILE):
            return
        if UserConfig.API not in cf.sections():
            return
        attrs = cf.options(UserConfig.API)

        for attr in attrs:
            if hasattr(self, self._name_attr2obj(attr)):
                setattr(self, self._name_attr2obj(attr), cf.get(UserConfig.API, attr))

    def _dump_config(self):
        objs = self._list_attrs()
        cf = CliConfigParser()

        cf.add_section(UserConfig.API)
        for obj in sorted(objs):
            cf.set(UserConfig.API, self._name_obj2attr(obj), objs[obj])

        with open(_USER_CONFIG_FILE, "w") as f:
            cf.write(f)

    def _list_attrs(self):
        attrs = vars(self)
        return {k : attrs[k]  for k in attrs if not k.startswith("_")}

    @staticmethod
    def _name_attr2obj(name):
        return name.replace("-", "_")

    @staticmethod
    def _name_obj2attr(name):
        return name.replace("_", "-")


if __name__ == '__main__':
    uc = UserConfig()
    #print uc.get_attrs({"secret-sssd": True, "region": False, "secret-key": "000000000"})
    #print uc.get_attrs({"secret-id": True, "region": True, "secret-key": "000000000"})
    #uc.set_attrs({"region":"asss-gz"})
    #uc.flush()
    print(uc.get_attrs({"region": True, "secret-key": "000000000"}))
