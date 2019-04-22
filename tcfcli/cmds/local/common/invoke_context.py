import json
import sys
import docker
import os

from tcfcli.libs.function.context import Context as FuncContext
from tcfcli.libs.function.fam_function_provider import ScfFunctionProvider
from tcfcli.libs.tcsam.tcsam import Resources
from tcfcli.libs.tcsam import model
from tcfcli.common.user_exceptions import InvokeContextException
from tcfcli.cmds.local.libs.local.local_runtime_manager import LocalRuntimeManager
from tcfcli.cmds.local.libs.local.debug_context import DebugContext


class InvokeContext(object):
    def __init__(self,
                 template_file,
                 function_identifier=None,
                 env_vars_file=None,
                 debug_port=None,
                 debug_args=None,
                 debugger_path=None,
                 docker_volume_basedir=None,
                 docker_network=None,
                 log_file=None,
                 skip_pull_image=None,
                 region=None,
                 namespace=None):

        self._template_file = template_file
        self._function_identifier = function_identifier
        self._env_vars_file = env_vars_file
        self._debug_port = debug_port
        self._debug_args = debug_args
        self._debugger_path = debugger_path
        self._docker_volume_basedir = docker_volume_basedir
        self._docker_network = docker_network
        self._log_file = log_file
        self._skip_pull_image = skip_pull_image
        self._region = region
        self.namespace = namespace

        self._template_dict = None
        self._function_provider = None
        self._env_vars = None
        self._log_file_fp = None
        self._debug_context = None

    def __enter__(self):
        template_dict = Resources(FuncContext().get_template_data(self._template_file)).to_json()
        resource = template_dict.get(model.RESOURCE, {})
        ns = resource.get(self.namespace, {})
        if not ns:
            raise InvokeContextException("You must provide a namespace identifier,default is 'default'")
        if model.TYPE in ns:
            del ns[model.TYPE]
        self._template_dict = {model.RESOURCE: ns}
        self._function_provider = ScfFunctionProvider(template_dict=self._template_dict)
        self._env_vars = self._get_env_vars(self._env_vars_file)
        self._log_file_fp = self._get_log_file(self._log_file)
        self._debug_context = self._get_debug_context(self._debug_port, self._debug_args, self._debugger_path)

        self._check_docker()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._log_file_fp:
            self._log_file_fp.close()

    def get_cwd(self):
        if self._docker_volume_basedir:
            cwd = self._docker_volume_basedir
        else:
            cwd = os.path.dirname(os.path.abspath(self._template_file))

        return cwd

    @property
    def local_runtime_manager(self):
        return LocalRuntimeManager(function_provider=self._function_provider,
                                   cwd=self.get_cwd(),
                                   env_vars=self._env_vars,
                                   debug_context=self._debug_context,
                                   region=self._region,
                                   docker_network_id=self._docker_network,
                                   skip_pull_image=self._skip_pull_image)

    @property
    def template(self):
        return self._template_dict

    @property
    def functions_name(self):
        if self._function_identifier:
            return self._function_identifier

        functions = [f for f in self._function_provider.get_functions()]
        if len(functions) == 1:
            return functions[0].name

        function_names = [f.name for f in functions]

        raise InvokeContextException("You must provide a function identifier (function's Logical ID in the template). "
                                     "Possible options in your template: {}".format(function_names))

    @property
    def stdout(self):
        if self._log_file_fp:
            return self._log_file_fp

        byte_stdout = sys.stdout

        if sys.version_info.major > 2:
            byte_stdout = sys.stdout.buffer

        return byte_stdout

    @property
    def stderr(self):
        if self._log_file_fp:
            return self._log_file_fp

        byte_stderr = sys.stderr

        if sys.version_info.major > 2:
            byte_stderr = sys.stderr.buffer

        return byte_stderr

    @staticmethod
    def _get_env_vars(env_vars_file):
        if env_vars_file is None:
            return None

        try:
            with open(env_vars_file, 'r') as fp:
                return json.load(fp)
        except Exception as e:
            raise InvokeContextException('read environment from file {} failed: {}'.format(env_vars_file, str(e)))

    @staticmethod
    def _get_log_file(log_file):
        if log_file is None:
            return

        return open(log_file, 'wb')

    @staticmethod
    def _get_debug_context(debug_port, debug_paras, debugger_path):
        return DebugContext(debug_port, debugger_path, debug_paras)

    @staticmethod
    def _check_docker(docker_client=None):
        docker_client = docker_client or docker.from_env()

        try:
            docker_client.ping()
        except Exception as e:
            raise InvokeContextException('Docker not found, please install it. %s' % e)
