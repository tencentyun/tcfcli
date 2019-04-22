import os
import sys
import json
import shutil
import tempfile
import zipfile
import click
import signal
import threading
from contextlib import contextmanager

from tcfcli.cmds.local.libs.docker.container import Container
from tcfcli.common.user_exceptions import InvalidEnvParameters


class LocalRuntime(object):
    _BASE_IMAGE_NAME = 'hub.tencentyun.com/qcloud_scf/scf'
    _GOLANG_SERVER_PORT = 33300
    _WORK_DIR = '/var/user'
    _CURRENT_DIR = '.'
    _BLANK = ''

    _ARCHIVE_FORMATS = ('.zip', '.ZIP')

    _RUNTIME_LIST = [
        'python2.7',
        'python3.6',
        'go1',
        'php5',
        'php7',
        'nodejs6.10',
        'nodejs8.9',
        'java8',
    ]

    def __init__(self, func_config, env_vars=None, cwd=None, debug_options=None, container_manager=None):
        self._func_config = func_config
        self._env_vars = env_vars
        self._cwd = cwd
        self._debug_options = debug_options
        self._container_manager = container_manager

        if self.get_runtime() not in self._RUNTIME_LIST:
            print(self.get_runtime())
            raise ValueError('Not support runtime {}'.format(self.get_runtime()))

        self._container = None

    def invoke(self, event=None, stdout=None, stderr=None):
        image = self.get_image()
        cmd = [self.get_handler()]
        code_abs_path = self.get_code_abs_path()
        memory = self.get_memory()
        entry = self.get_entry_point()
        ports ={self._debug_options.debug_port: self._debug_options.debug_port} \
            if self._debug_options else None
        envs = self.get_envs(event)
        timer = None

        with self._get_code(code_abs_path) as code_dir:
            self._container = Container(image=image,
                                        cmd=cmd,
                                        work_dir=self._WORK_DIR,
                                        host_dir=code_dir,
                                        mem=memory,
                                        env_vars=envs,
                                        entrypoint=entry,
                                        ports=ports)

            try:
                self._container_manager.run(self._container)

                timer = self._wait_timeout(self._container, self.get_timeout(), bool(self._debug_options))

                self._container.get_logs(stdout=stdout, stderr=stderr)

            except KeyboardInterrupt:
                click.secho('Abort function execution')
            except Exception as err:
                click.secho('Invoke error:%s' % str(err))

            finally:
                if timer:
                    timer.cancel()
                self._container.delete()

    def get_func_name(self):
        return self._func_config.name

    def get_image(self):
        runtime = self.get_runtime()
        return '%s:%s' % (self._BASE_IMAGE_NAME, runtime)

    def get_runtime(self):
        return self._func_config.runtime.lower()

    def get_handler(self):
        res = self._func_config.handler.split('.', 1)
        if len(res) > 1:
            return res[0] + ':' + res[1]
        return res[0]

    def get_golang_port(self):
        return self._GOLANG_SERVER_PORT

    def get_code_uri(self):
        return self._func_config.codeuri

    def get_memory(self):
        return self._func_config.memory

    def get_timeout(self):
        return int(self._func_config.timeout)

    def get_entry_point(self):
        if not self._debug_options:
            return None

        runtime = self.get_runtime()
        if runtime not in ["nodejs6.10", "nodejs8.9"]:
            raise InvalidEnvParameters("Debugging is not currently supported for {}".format(runtime))

        debug_port = self._debug_options.debug_port
        debug_args = self._debug_options.debug_args
        debug_args_list = []
        if debug_args:
            debug_args_list = debug_args.split(" ")

        entrypoint = None
        if runtime == "nodejs6.10":
            entrypoint = ["/var/lang/node6/bin/node"] \
                   + debug_args_list \
                   + [
                       "--inspect",
                       "--debug-brk=" + str(debug_port),
                       "--nolazy",
                       "--max-old-space-size=2547",
                       "--max-semi-space-size=150",
                       "--max-executable-size=160",
                       "--expose-gc",
                       "/var/runtime/node6/bootstrap.js",
                   ]
        elif runtime == "nodejs8.9":
            entrypoint = ["/var/lang/node8/bin/node"] \
                    + debug_args_list \
                    + [
                        "--inspect-brk=0.0.0.0:" + str(debug_port),
                        "--nolazy",
                        "--expose-gc",
                        "--max-semi-space-size=150",
                        "--max-old-space-size=2707",
                        "/var/runtime/node8/bootstrap.node8.js",
                    ]
        return entrypoint

    def get_code_abs_path(self):
        # return the code path based on current working directory

        if not self._cwd or self._cwd == self._CURRENT_DIR:
            self._cwd = os.getcwd()

        self._cwd = os.path.abspath(self._cwd)

        code_path = self.get_code_uri()
        if not os.path.isabs(self.get_code_uri()):
            code_path = os.path.normpath(os.path.join(self._cwd, code_path))

        return code_path

    def get_envs(self, event=None):
        func_name = self._func_config.name
        variables = None
        if self._func_config.environment and isinstance(self._func_config.environment, dict) and 'Variables' in self._func_config.environment:
            variables = self._func_config.environment['Variables']

        for env_var in self._env_vars.values():
            if not isinstance(env_var, dict):
                raise InvalidEnvParameters('Environment variables format is invalid, format must like as {FunctionName: {key: value} JSON pairs}')

        overrides = self._env_vars.get(func_name, None)

        return self.generate_runtime_envs(variables, overrides, event)

    def generate_runtime_envs(self, template_env, overrides, event):
        template_env_values = template_env or {}
        overrides_values = overrides or {}

        env_set = {
            'SCF_LOCAL': 'true',
            '_SCF_SERVER_PORT': str(self.get_golang_port()),
            '_LAMBDA_SERVER_PORT': str(self.get_golang_port()),
            'SCF_FUNCTION_NAME': self.get_func_name(),
            'SCF_FUNCTION_MEMORY_SIZE': str(self.get_memory()),
            'SCF_FUNCTION_TIMEOUT': str(self.get_timeout()),
            'SCF_FUNCTION_HANDLER': self.get_handler(),

            'SCF_EVENT_BODY': '{}'
        }

        environ = {}
        for key, value in template_env_values.items():
            if key in overrides_values:
                value = overrides_values[key]

            environ[key] = value
            env_set[key] = self._stringfy(value)

        env_set['SCF_FUNCTION_ENVIRON'] = json.dumps(environ)

        if event:
            env_set['SCF_EVENT_BODY'] = event

        return env_set

    def _stringfy(self, value):
        if isinstance(value, (dict, tuple, list)) or value is None:
            res = self._BLANK
        elif value is True:
            res = 'true'
        elif value is False:
            res = 'false'
        elif sys.version_info.major > 2:
            res = str(value)
        elif not isinstance(value, unicode):
            res = str(value)
        else:
            res = value

        return res

    @contextmanager
    def _get_code(self, code_abs_path):
        tmp_code_path = None

        try:
            if os.path.isfile(code_abs_path) and code_abs_path.endswith(self._ARCHIVE_FORMATS):
                tmp_code_path = self._get_tmp_code_path(code_abs_path)
                yield tmp_code_path
            else:
                yield code_abs_path
        finally:
            if tmp_code_path:
                shutil.rmtree(tmp_code_path)

    def _get_tmp_code_path(self, code_abs_path):
        tmp_dir = tempfile.mkdtemp()

        if os.name == 'posix':
            os.chmod(tmp_dir, 0o755)

        self._unzip(code_abs_path, tmp_dir)

        return os.path.realpath(tmp_dir)

    def _unzip(self, source_file, target_dir):
        with zipfile.ZipFile(source_file, 'r') as f:
            for file in f.namelist():
                f.extract(file, target_dir)

    def _wait_timeout(self, container=None, timeout=None, isdebug=False):
        if not timeout:
            timeout = 3

        def signal_handler(sig, frame):
            container.delete()

        def stop_container():
            click.secho('Function "%s" timeout after %d seconds' % (self.get_func_name(), timeout))
            container.delete()

        if isdebug:
            signal.signal(signal.SIGTERM, signal_handler)
            return

        timer = threading.Timer(timeout, stop_container)
        timer.start()

        return timer