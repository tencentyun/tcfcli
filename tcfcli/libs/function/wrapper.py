import copy
from tcfcli.libs.function.provider import TENCENT_FUNCTION_TYPE
from tcfcli.common.user_exceptions import InvalidDocumentException, InvalidTemplateException


class TemplateReimplemented(object):
    def __init__(self, template_dict):
        self._glob = None
        self._glob_settings = None
        self._resources = None
        self._template = copy.deepcopy(template_dict)

    def parse(self):
        try:
            self._validate()
            if self._glob_settings:
                self._merge_globals()

            return self._template
        except InvalidDocumentException as e:
            raise e

    def _validate(self):
        # basic validate, future will add restrict validate
        if not TemplateReimplemented._check_key_exist("Resources", self._template):
            raise InvalidTemplateException("'Resources' section is required")

        if len(self._template["Resources"]) < 1:
            raise InvalidTemplateException("Function not found in the template")

        self._resources = self._template["Resources"]
        for logic_id in self._resources:
            if "Type" not in self._resources[logic_id]:
                raise InvalidTemplateException("Resource '{}' define error: Lost 'Type' properties".format(logic_id))

            if self._resources[logic_id]["Type"] != TENCENT_FUNCTION_TYPE:
                raise InvalidTemplateException("Resource '{}' define error: Must define the resource 'Type' like as "
                                               "'{}'".format(logic_id, TENCENT_FUNCTION_TYPE))

            if not TemplateReimplemented._check_key_exist("Properties", self._resources[logic_id]):
                raise InvalidTemplateException("Resource '{}' define error: Must define the resource 'Properties'".
                                               format(logic_id))

            if TemplateReimplemented._check_key_exist("Events", self._resources[logic_id]["Properties"]):
                self._check_events_valid(logic_id, self._resources[logic_id]["Properties"]["Events"])

        if TemplateReimplemented._check_key_exist("Globals", self._template):
            self._glob = self._template["Globals"]
            if TemplateReimplemented._check_key_exist("Function", self._glob):
                self._glob_settings = self._glob["Function"]
                TemplateReimplemented._check_properties_valid(self._glob_settings, "Globals")

    def _merge_globals(self):
        for func_name in self._resources:
            func_settings = self._template["Resources"][func_name]["Properties"].copy()
            glob_settings = copy.deepcopy(self._glob_settings)
            glob_settings.update(func_settings)
            func_settings.update(glob_settings)
            self._template["Resources"][func_name]["Properties"] = func_settings

    @staticmethod
    def _check_key_exist(key, dict_map):
        if key not in dict_map or not isinstance(dict_map[key], dict) or\
                not dict_map[key]:
            return False
        return True

    @staticmethod
    def _check_properties_valid(dict_map, blob):
        if "Environment" in dict_map:
            TemplateReimplemented._check_env_valid(dict_map["Environment"], blob)

        if "VpcConfig" in dict_map:
            TemplateReimplemented._check_vpc_valid(dict_map["VpcConfig"], blob)

        if "FunctionName" in dict_map:
            raise InvalidTemplateException("Can not define 'FunctionName' in Globals block")

        if "CodeUri" in dict_map:
            raise InvalidTemplateException("Can not define 'CodeUri' in Globals block")

        if "Events" in dict_map:
            raise InvalidTemplateException("Can not define 'Events' in Globals block")

    @staticmethod
    def _check_env_valid(dict_map, blob):
        if not TemplateReimplemented._check_key_exist("Variables", dict_map):
            raise InvalidTemplateException("Has Environment but not define Variables in '{}'".format(blob))

        if len(dict_map["Variables"]) < 1:
            raise InvalidTemplateException("Environment values in '{}' not defined".format(blob))

    @staticmethod
    def _check_vpc_valid(dict_map, blob):
        if not TemplateReimplemented._check_key_exist("VpcId", dict_map):
            raise InvalidTemplateException("VpcId not found in '{}'".format(blob))

        if not TemplateReimplemented._check_key_exist("SubnetId", dict_map):
            raise InvalidTemplateException("SubnetTd not found in '{}'".format(blob))

    @staticmethod
    def _check_events_valid(func, dict_map):
        for event_id, config in dict_map.items():
            if "Type" not in config:
                raise InvalidTemplateException("Events 'Type' not found in Resource '{}'".format(func))

            if config["Type"] != 'Api':
                raise InvalidTemplateException("Events 'Type' not equal 'Api' in Resource '{}'".format(func))

            if "Properties" not in config:
                raise InvalidTemplateException("Events 'Properties' not found in Resource '{}'".format(func))

            if "Path" not in config["Properties"]:
                raise InvalidTemplateException("Api Path not found in Event from Resource '{}'".format(func))

            if "Method" not in config["Properties"]:
                raise InvalidTemplateException("Api Method not found in Event from Resource '{}'".format(func))

            if "StageName" in config["Properties"]:
                # TODO: if check?
                pass
