import io
import json
from tcfcli.common.user_exceptions import InvalidEnvVarsException

class FileUtil(object):

    @staticmethod
    def load_json_from_file(p):
        if p is None:
            return {}
        try:
            with io.open(p, mode='r', encoding='utf-8') as fp:
                return json.load(fp)
        except Exception as e:
            raise InvalidEnvVarsException('read environment from file {} failed: {}'.format(p, str(e)))