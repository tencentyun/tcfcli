from __future__ import print_function
import os
import sys
import json
import time
import uuid
import pstool

tcf_stdout = sys.stdout
tcf_stderr = sys.stderr

_GLOBAL_START_TIME = time.time()
_GLOBAL_SOCK = -1
_GLOBAL_STAGE = 0

_GLOBAL_REQUEST_ID = str(uuid.uuid4())
_GLOBAL_FUNCTION_NAME = os.environ.get('SCF_FUNCTION_NAME', 'test')
_GLOBAL_VERSION = os.environ.get('SCF_FUNCTION_VERSION', '$LATEST')
_GLOBAL_MEM_SIZE = os.environ.get('SCF_FUNCTION_MEMORY_SIZE', '256')
_GLOBAL_TIMEOUT = int(os.environ.get('SCF_FUNCTION_TIMEOUT', '3'))

_GLOBAL_FUNCTION_HANDLER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('SCF_FUNCTION_HANDLER',
        'index:main_handler')

_GLOBAL_EVENT_BODY =  sys.argv[2] if len(sys.argv) > 2 else os.environ.get('SCF_EVENT_BODY',
        (sys.stdin.read() if os.environ.get('DOCKER_USE_STDIN', False) else '{}'))


def init():
    tcf_print("START RequestId: %s" % _GLOBAL_REQUEST_ID)

    os.environ['SOCKETPATH'] = ''
    os.environ['CONTAINERID'] = ''

    return 0



def init_context():
    context = {}

    context['environ'] = ""
    context['request_id'] = _GLOBAL_REQUEST_ID

    context['function_version'] = _GLOBAL_VERSION
    context['function_name'] = _GLOBAL_FUNCTION_HANDLER

    context['time_limit_in_ms'] = _GLOBAL_TIMEOUT
    context['memory_limit_in_mb'] = _GLOBAL_MEM_SIZE

    return json.dumps(context)


class InvokeInfo(object):
    pass


def wait_for_invoke():
    global _GLOBAL_STAGE
    _GLOBAL_STAGE += 1

    invoke_info = InvokeInfo()
    if _GLOBAL_STAGE == 1:
        invoke_info.cmd = 'RELOAD'
        invoke_info.sockfd = _GLOBAL_SOCK
        invoke_info.event =_GLOBAL_EVENT_BODY
        invoke_info.context = _GLOBAL_FUNCTION_HANDLER
    elif _GLOBAL_STAGE == 2:
        invoke_info.cmd = 'EVENT'
        invoke_info.sockfd = _GLOBAL_SOCK
        invoke_info.event = _GLOBAL_EVENT_BODY
        invoke_info.context = init_context()
    else:
        os._exit(0)

    return invoke_info


def report_done(msg, err_type=0):
    tcf_print("END RequestId: %s" % _GLOBAL_REQUEST_ID)

    duration = int((time.time() - _GLOBAL_START_TIME) * 1000)
    billed_duration = min(100 * int((duration / 100) + 1), _GLOBAL_TIMEOUT * 1000)
    max_mem = pstool.get_peak_memory()  # memory use in MB
    tcf_print(
        "REPORT RequestId: %s Duration: %s ms Billed Duration: %s ms Memory Size: %s MB Max Memory Used: %s MB" % (
            _GLOBAL_REQUEST_ID, duration, billed_duration, _GLOBAL_MEM_SIZE, max_mem
        )
    )

    tcf_print("\n")

    if msg:
        tcf_print("%s" % msg)


def report_running():
    global _GLOBAL_START_TIME
    _GLOBAL_START_TIME = time.time()


def report_fail(stackTrace, mem_kb, ret_code):
    result = {}
    result['errorCode'] = 1
    result['errorMessage'] = 'user code exception caught'
    if stackTrace:
        result['stackTrace'] = stackTrace

    report_done('')
    tcf_print(result)


def console_log(errMsg):
    tcf_print(errMsg)


def log(errMsg):
    pass


def tcf_print(*args, **kwargs):
    print(*args, file=tcf_stderr, **kwargs)
