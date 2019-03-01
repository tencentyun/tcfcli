import os
import yaml
from tcfcli.common.user_exceptions import ContextException
from tcfcli.libs.function.fam_function_provider import ScfFunctionProvider
from tcfcli.libs.utils.yaml_parser import yaml_parse


class Context(object):
    def __init__(self, template_file=None, cos_bucket=None, output_template_file=None):
        self._template_file = template_file
        self._output_template_file = output_template_file
        self._cos_bucket = cos_bucket

        self._template_dict = None

    def __enter__(self):
        if self._template_file:
            self._template_dict = self.get_template_data(self._template_file)
            self._function_provider = ScfFunctionProvider(self._template_dict)
            self._functions = self._function_provider.get_all()
            self._deploy_template = self._function_provider.deploy_template

        return self

    def __exit__(self, *args):
        pass

    @property
    def template(self):
        return self._template_dict

    @property
    def template_path(self):
        return self._template_file

    @property
    def cos_bucket(self):
        return self._cos_bucket

    @property
    def output_template_file_path(self):
        return self._output_template_file

    @staticmethod
    def get_template_data(template_file):
        if not os.path.exists(template_file):
            return {}

        with open(template_file, 'r') as f:
            try:
                return yaml_parse(f.read())
            except (ValueError, yaml.YAMLError) as ex:
                raise ContextException("Parse template failed: {}".format(str(ex)))
        return

    def get_functions(self):
        for _, func in self._functions.items():
            yield func

    @property
    def deploy_template(self):
        return self._deploy_template
