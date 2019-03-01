from copy import deepcopy


class ApiProvider(object):

    _RESOURCE = 'Resources'
    _PROPERTIES = 'Properties'
    _EVENTS = 'Events'
    _PATH = 'Path'
    _METHOD = 'Method'

    _ANY_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'ANY']

    def __init__(self, template):
        self._template = deepcopy(template)
        self._resources = self._template.get(self._RESOURCE, {})
        self.apis = self._extract_apis(self._resources)

    def get_all(self):
        for api in self.apis:
            yield api

    def _extract_apis(self, resources):
        apis = []

        for func_name, resource in resources.items():
            if self._EVENTS in resource[self._PROPERTIES]:
                for event, config in resource[self._PROPERTIES][self._EVENTS].items():
                    path = config[self._PROPERTIES].get(self._PATH, None)
                    method = config[self._PROPERTIES].get(self._METHOD, None)

                    api = API(path, method, func_name)
                    apis.append(api)

        return ApiProvider._normalize_apis(apis)

    @staticmethod
    def _normalize_apis(apis):
        res = []

        for api in apis:
            for normal_method in ApiProvider._normalize_method(api.method):
                res.append(API(path=api.path, method=normal_method, func_name=api.func_name))

        return res

    @staticmethod
    def _normalize_method(api_method):
        if api_method.upper() == 'ANY':
            for method in ApiProvider._ANY_METHODS:
                yield method
        else:
            yield api_method.upper()


class API(object):
    def __init__(self, path, method, func_name, ):
        self.path = path
        self.method = method
        self.func_name = func_name

