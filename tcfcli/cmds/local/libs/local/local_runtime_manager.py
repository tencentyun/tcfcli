from tcfcli.cmds.local.libs.docker.manager import ContainerManager
from tcfcli.cmds.local.libs.local.local_runtime import LocalRuntime
from tcfcli.common.user_exceptions import FunctionNotFound


class LocalRuntimeManager(object):
    def __init__(self,
                 function_provider,
                 cwd,
                 env_vars=None,
                 debug_context=None,
                 region=None,
                 docker_network_id=None,
                 skip_pull_image=False):

        self._provider = function_provider
        self._cwd = cwd
        self._env_vars = env_vars or {}
        self._region = region
        self._debug_context = debug_context

        self._container_manager = ContainerManager(docker_network_id, skip_pull_image)

    def invoke(self, func_name, event=None, stdout=None, stderr=None):
        local_runtime = LocalRuntime(func_config=self._get_func_config(func_name),
                                     env_vars=self._env_vars,
                                     cwd=self._cwd,
                                     debug_options=self.debug_options,
                                     container_manager=self._container_manager)

        local_runtime.invoke(event, stdout=stdout, stderr=stderr)

    def _get_func_config(self, func_name):
        func_config = self._provider.get(func_name)

        if not func_config:
            raise FunctionNotFound('function with name "%s" not found' % func_name)

        return func_config

    @property
    def debug_options(self):
        return self._debug_context
