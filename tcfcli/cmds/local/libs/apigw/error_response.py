from flask import make_response, jsonify


class ErrorResponse(object):

    _INTERNAL_ERROR = {'errorMessage': 'Internal error'}
    _NOT_FOUND_BIND_FUNC = {'errorMessage': 'Not found the function bind to the route'}
    _INVALID_RESPONSE_FORMAT = {'errno': 403, 'error': 'Invalid scf response format. please check your scf response format.'}

    _STATUS_CODE_403 = 403
    _STATUS_CODE_502 = 502

    @staticmethod
    def InternalError(msg=None):
        err_msg = ErrorResponse._INTERNAL_ERROR

        if msg and isinstance(msg, str):
            err_msg = {'errorMessage': msg}

        return make_response(jsonify(err_msg), ErrorResponse._STATUS_CODE_502)

    @staticmethod
    def FuncNotFound(msg=None):
        err_msg = ErrorResponse._NOT_FOUND_BIND_FUNC

        if msg and isinstance(msg, str):
            err_msg = {'errorMessage': msg}

        return make_response(jsonify(err_msg), ErrorResponse._STATUS_CODE_403)

    @staticmethod
    def InvalidResponseFormat(msg=None):
        err_msg = ErrorResponse._INVALID_RESPONSE_FORMAT

        if msg and isinstance(msg, str):
            err_msg = {'errorMessage': msg}

        return make_response(jsonify(err_msg), ErrorResponse._STATUS_CODE_403)