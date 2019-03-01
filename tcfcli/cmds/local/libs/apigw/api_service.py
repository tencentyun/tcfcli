import os
import logging
from tcfcli.libs.apis.provider import ApiProvider
from tcfcli.cmds.local.libs.apigw.local_service import LocalService, Route
from tcfcli.common.user_exceptions import NoApiDefinition

logger = logging.getLogger(__name__)


class LocalApiService(object):

    _DEFAULT_PORT = 3000
    _DEFAULT_HOST = '127.0.0.1'

    def __init__(self, invoke_context, port=None, host=None, static_dir=None):
        self._invoke_context = invoke_context
        self._stderr = invoke_context.stderr
        self._port = port or self._DEFAULT_PORT
        self._host = host or self._DEFAULT_HOST
        self._static_dir = static_dir

        self._local_runtime_manager = invoke_context.local_runtime_manager
        self._api_provider = ApiProvider(invoke_context.template)

    def start(self):
        routes_list = self._get_routes()

        if not routes_list:
            raise NoApiDefinition('There is no api definition in template')

        static_dir_path = self._get_static_dir_path()

        svc = LocalService(routes_list=routes_list,
                           runtime_manager=self._local_runtime_manager,
                           static_dir=static_dir_path,
                           port=self._port,
                           host=self._host,
                           stderr=self._stderr)

        self._show_routes(routes_list, port=self._port, host=self._host)
        logger.info('Mounting finsh. You can browse to the above endpoints to invoke functions. Support modify function code online, only need to restart tcf when the template changed.')

        svc.listen()

    def _get_routes(self):
        routes = []

        for api in self._api_provider.get_all():
            route = Route(method=[api.method], path=api.path, func_name=api.func_name)
            routes.append(route)

        return routes

    def _show_routes(self, routes_list, port, host):
        for route in routes_list:
            if route.method[0] is not 'ANY':
                logger.info('Mounting {} at http://{}:{}{} {}'.format(route.func_name, host, port, route.path, route.method))

    def _get_static_dir_path(self):
        if not self._static_dir:
            return None

        cwd = self._invoke_context.get_cwd()

        static_dir_path = os.path.join(cwd, self._static_dir)
        if os.path.exists(static_dir_path):
            return staticmethod

        return None
