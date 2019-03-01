import sys

PY_2 = 2
PY_3 = 3
pyv = sys.version_info
version = PY_2
if pyv[0] == PY_3:
    version = PY_3


def url_encoding(data):
    if version == PY_2:
        import urllib
        return urllib.quote(data)
    from urllib import parse
    return parse.quote(data)

