import io
import os
import sys
import json
import uuid
import base64
import logging

from flask import Flask, Response, request
from tcfcli.cmds.local.libs.apigw.path_converter import PathConverter
from tcfcli.cmds.local.libs.events.api import ApigwEvent
from tcfcli.cmds.local.libs.apigw.error_response import ErrorResponse

logger = logging.getLogger(__name__)


class LocalService(object):
    def __init__(self, routes_list, runtime_manager, static_dir=None, port=None, host=None, stderr=None):
        self._routes_list = routes_list
        self._runtime_manager = runtime_manager
        self._static_dir = static_dir
        self._port = port
        self._host = host
        self._stderr = stderr

        self._route_map = {}
        self._server = None

    def create(self):
        self._server = Flask(__name__, static_url_path='', static_folder=self._static_dir)

        for route in self._routes_list:
            path = PathConverter.convert_path_to_flask(route.path)
            self._save_route_map(path, route)
            self._server.add_url_rule(path,
                                      endpoint=path,
                                      methods=route.method,
                                      view_func=self._request_handler,
                                      provide_automatic_options=False)

    def listen(self):
        self.create()

        if not self._server:
            raise RuntimeError('Local service has not been created before listening')

        os.environ['WERKZEUG_RUN_MAIN'] = 'true'

        self._server.run(threaded=True, host=self._host, port=self._port)

    def _request_handler(self, **kwargs):
        key = request.path + ':' + request.method

        if key not in self._route_map.keys():
            raise RuntimeError('Not found the function bind to the route')

        try:
            event = self._generate_api_event(request)
        except UnicodeDecodeError:
            return ErrorResponse.InternalError()

        stdout = io.BytesIO()
        try:
            self._runtime_manager.invoke(self._route_map[key].func_name,
                                         event,
                                         stdout=stdout,
                                         stderr=self._stderr)
        except:
            return ErrorResponse.InternalError()

        return_value, log_list= self._get_ouput(stdout)

        if self._stderr and log_list:
            for line in log_list:
                if sys.version_info.major > 2:
                    self._stderr.write(bytes(line + '\n', encoding='utf-8'))
                else:
                    self._stderr.write(bytes(line + '\n').encode("utf-8"))

        try:
            status_code, headers, body = self._parse_output(return_value)
        except TypeError as ex:
            logging.error('parse return value error: {}'.format(str(ex)))
            return ErrorResponse.InvalidResponseFormat()

        return self._response(status_code, headers, body)

    def _save_route_map(self, path=None, route=None):
        if not route or not path:
            return

        for method in route.method:
            key = '{}:{}'.format(path, method)
            self._route_map[key] = route

    @staticmethod
    def _generate_api_event(request):
        req_context = {
            'path': PathConverter.convert_path_to_api_gateway(request.endpoint),
            'httpMethod': request.method,
            'requestId': str(uuid.uuid1()),
            'sourceIp': request.remote_addr,
            'stage': 'prod',
        }

        headers = dict(request.headers)

        body = request.get_data()
        if body:
            body = body.decode('utf-8')

        queries = LocalService._generate_query_dict(request)

        event = ApigwEvent(method=request.method,
                           path=request.path,
                           path_paras=request.view_args,
                           body=body,
                           headers=headers,
                           req_context=req_context,
                           queries_dict=queries)

        return event.to_str()

    @staticmethod
    def _generate_query_dict(request):
        query_dict = {}

        for query_key, query_values in request.args.lists():
            query_values_num = len(query_values)

            if not query_values_num:
                query_dict[query_key] = ""
            else:
                query_dict[query_key] = query_values[-1]

        return query_dict

    @staticmethod
    def _get_ouput(stdout_stream):
        output = stdout_stream.getvalue().decode('utf-8').strip('\n').split('\n')

        output_length = len(output)
        log_list = None
        if output_length > 1:
            log_list = output[:output_length - 1]

        return_value = output[-1]

        return return_value, log_list

    @staticmethod
    def _parse_output(return_vlue):
        try:
            return_json = json.loads(return_vlue)
        except:
            raise TypeError('return value must be a valid json')

        if not isinstance(return_json, dict):
            raise TypeError('return value must be a valid json, not "{}"'.format(type(return_json)))

        status_code = return_json.get('statusCode') or None
        headers = return_json.get('headers') or None
        body = return_json.get('body') or ''
        is_base64_encoded = return_json.get('isBase64Encoded') or False

        if not isinstance(status_code, int) or status_code <= 0:
            raise TypeError('statusCode must be positive int')

        if not isinstance(headers, dict) or headers is None:
            raise TypeError('headers format is wrong')

        if is_base64_encoded:
            body = base64.b64decode(body)

        if 'Content-type' not in headers:
            headers['type'] = 'application/json'

        return status_code, headers, body

    @staticmethod
    def _response(status_code, headers, body):
        response = Response(body)
        response.headers = headers
        response.status_code = status_code

        return response


class Route(object):
    def __init__(self, method, path, func_name):
        self.method = method
        self.path = path
        self.func_name = func_name
