import json

class ApigwEvent(object):
    def __init__(self,
                 method=None,
                 path=None,
                 body=None,
                 headers=None,
                 req_context=None,
                 queries_dict=None,
                 path_paras=None):

        if not isinstance(headers, dict) and headers is not None:
            raise TypeError('queries_dict is not dict or None' )

        if not isinstance(req_context, dict) and req_context is not None:
            raise TypeError('req_context is not dict or None' )

        if not isinstance(queries_dict, dict) and queries_dict is not None:
            raise TypeError('queries_dict is not dict or None' )

        if not isinstance(path_paras, dict) and path_paras is not None:
            raise TypeError('path_paras is not dict or None' )

        self._method = method
        self._path = path
        self._body = body
        self._headers = headers
        self._req_context = req_context
        self._queries_dict = queries_dict
        self._path_paras = path_paras

    def to_dict(self):
        self._event_dict = {
            'httpMethod': self._method,
            'path': self._path,
            'requestContext': self._req_context,
            'headersParameters': dict(self._headers) if self._headers else {},
            'pathParameters': dict(self._path_paras) if self._path_paras else {},
            'queryStringParameters': dict(self._queries_dict) if self._queries_dict else {},

        }

        if self._body:
            self._event_dict['body'] = self._body

        return self._event_dict

    def to_str(self):
        return json.dumps(self.to_dict())
