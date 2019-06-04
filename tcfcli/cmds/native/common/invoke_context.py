import json
import sys
import os
import click
import subprocess
import threading
from tcfcli.common import tcsam
from tcfcli.common.tcsam.tcsam_macro import TcSamMacro as tsmacro
from tcfcli.common.user_exceptions import InvokeContextException
from tcfcli.common.user_exceptions import InvalidOptionValue
from tcfcli.cmds.native.common.runtime import Runtime
from tcfcli.cmds.native.common.debug_context import DebugContext
from tcfcli.common.template import Template
from tcfcli.common.macro import MacroRuntime
from tcfcli.common.file_util import FileUtil

class InvokeContext(object):

    BOOTSTRAP_SUFFIX = {
        MacroRuntime.node610: "bootstrap.js",
        MacroRuntime.node89: "bootstrap.js",
        MacroRuntime.python27: "bootstrap.py",
        MacroRuntime.python36: "bootstrap.py",
    }

    def __init__(self,
                 template_file,
                 function=None,
                 namespace=None,
                 env_file=None,
                 debug_port=None,
                 debug_args="",
                 event="{}"):

        self._template_file = template_file
        self._function = function
        self._namespace = namespace
        self._event = event
        self._debug_port = debug_port
        self._debug_argv = debug_args
        self._runtime = None
        self._debug_context = None
        self._env_file = env_file

    def _get_namespace(self, resource):
        ns = None
        if self._namespace:
            ns = resource.get(self._namespace, None)
        else:
            nss = list(resource.keys())
            if len(nss) == 1:
                self._namespace = nss[0]
                ns = resource.get(nss[0], None)
        if not ns:
            raise InvokeContextException("You must provide a valid namespace")

        del ns[tsmacro.Type]
        return ns

    def _get_function(self, namespace):
        fun = None
        if self._function:
            fun = namespace.get(self._function, None)
        else:
            funs = list(namespace.keys())
            if len(funs) == 1:
                self._function = funs[0]
                fun = namespace.get(funs[0], None)
        if not fun:
            raise InvokeContextException("You must provide a valid function")

        del fun[tsmacro.Type]
        return fun

    def __enter__(self):
        template_dict = tcsam.tcsam_validate(Template.get_template_data(self._template_file))

        resource = template_dict.get(tsmacro.Resources, {})
        func = self._get_function(self._get_namespace(resource))
        self._runtime = Runtime(func.get(tsmacro.Properties, {}))
        self._debug_context = DebugContext(self._debug_port, self._debug_argv, self._runtime.runtime)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def invoke(self):
        def timeout_handle(child):
            try:
                click.secho('Function "%s" timeout after %d seconds' % (self._function, self._runtime.timeout))
                child.kill()
            except Exception:
                pass
        try:
            child = subprocess.Popen(args=[self.cmd]+self.argv, env=self.env)
        except OSError:
            click.secho("Execution failed,confirm whether the program({}) is installed".format(self._runtime.cmd))
            return
        timer = threading.Timer(self._runtime.timeout, timeout_handle, [child])
        if not self._debug_context.is_debug:
            timer.start()
        child.wait()
        timer.cancel()

    @property
    def cmd(self):
        return self._debug_context.cmd if \
            self._debug_context.cmd is not None \
            else self._runtime.cmd

    @property
    def argv(self):
        argv = self._debug_context.argv
        runtime_pwd = os.path.dirname(os.path.abspath(__file__))
        bootstrap = os.path.join(runtime_pwd, "runtime", self._runtime.runtime,
                            self.BOOTSTRAP_SUFFIX[self._runtime.runtime])
        code = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(self._template_file)), self._runtime.codeuri))
        return argv + [bootstrap, os.path.join(code, self.get_handler())]

    @property
    def env(self):
        env = {
            'SCF_LOCAL': 'true',
            'SCF_FUNCTION_MEMORY_SIZE': str(self._runtime.mem_size),
            'SCF_FUNCTION_TIMEOUT': str(self._runtime.timeout),
            'SCF_EVENT_BODY': self._event,
            'SCF_FUNCTION_ENVIRON': json.dumps(self._runtime.env)
        }

        for k, v in self._runtime.env.items():
            env[k] = v

        for k, v in os.environ.items():
            env[k] = v

        env.update(FileUtil.load_json_from_file(self._env_file))
        return env

    def get_handler(self):
        res = self._runtime.handler.split('.', 1)
        if len(res) > 1:
            return res[0] + ':' + res[1]
        return res[0]
