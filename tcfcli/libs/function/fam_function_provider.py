import logging
import copy
from tcfcli.libs.function.provider import FunctionProvider, TENCENT_FUNCTION_TYPE, Function
from tcfcli.libs.function.wrapper import TemplateReimplemented

logger = logging.getLogger(__name__)


class ScfFunctionProvider(FunctionProvider):

    _TENCENT_FUNCTION = TENCENT_FUNCTION_TYPE
    _DEFAULT_CODEURI = "."
    _DEFAULT_RUNTIME = "python2.7"
    _DEFAULT_HANDLER = "index.main_handler"
    _DEFAULT_TIMOUT_SECONDS = 3
    _DEFAULT_MEMORY = 128

    def __init__(self, template_dict):
        self.template_dict = self.get_final_template(template_dict)
        self.resources = self.template_dict.get("Resources", {})
        if len(self.resources) > 1:
            logger.debug("There are %d function resources found in the template", len(self.resources))

        self.functions = self._extract_functions(self.resources)

    def get(self, name):
        if not name:
            raise ValueError("Function name is required")

        return self.functions.get(name)

    def get_all(self):
        return self.functions

    def get_functions(self):
        for _, func in self.functions.items():
            yield func

    @staticmethod
    def get_final_template(template_dict):
        template_dict = template_dict or {}
        # if template_dict:
        #    template_dict = TemplateReimplemented(template_dict).parse()
        return template_dict

    @staticmethod
    def _extract_functions(resources):
        result = {}

        for name, resource in resources.items():
            resource_properties = resources[name].get("Properties", {})
            result[name] = ScfFunctionProvider._convert_fam_function_resource(name, resource_properties)

        return result

    @staticmethod
    def _convert_fam_function_resource(name, resource_properties):
        codeuri = resource_properties.get("CodeUri", ScfFunctionProvider._DEFAULT_CODEURI)
        cos_bucket_name = resource_properties.get("CosBucketName")
        cos_object_name = resource_properties.get("CosObjectName")
        zip_file = resource_properties.get("LocalZipFile")

        return Function(
            name=name,
            runtime=resource_properties.get("Runtime", ScfFunctionProvider._DEFAULT_RUNTIME),
            memory=resource_properties.get("MemorySize", ScfFunctionProvider._DEFAULT_MEMORY),
            timeout=resource_properties.get("Timeout", ScfFunctionProvider._DEFAULT_TIMOUT_SECONDS),
            handler=resource_properties.get("Handler", ScfFunctionProvider._DEFAULT_HANDLER),
            description=resource_properties.get("Description"),
            codeuri=codeuri,
            cos_bucket_name=cos_bucket_name,
            cos_object_name=cos_object_name,
            zip_file=zip_file,
            environment=resource_properties.get("Environment"),
            vpc=resource_properties.get("VpcConfig")
        )

    @property
    def deploy_template(self):
        template_dict = copy.deepcopy(self.template_dict)
        if "Globals" in template_dict:
            del template_dict["Globals"]

        return template_dict
