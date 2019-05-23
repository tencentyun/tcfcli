from tcfcli.common.user_exceptions import InvalidOptionValue
from tcfcli.common.macro import MacroRuntime


class DebugContext(object):

    DEBUG_CMD = {
        MacroRuntime.node610: MacroRuntime.cmd_node610,
        MacroRuntime.node89: MacroRuntime.cmd_node89,
        MacroRuntime.python27: MacroRuntime.cmd_python27,
        MacroRuntime.python36: MacroRuntime.cmd_python36
    }

    def __init__(self, port, argv, runtime):
        self.debug_port = port
        self.debug_argv = argv
        self.runtime = runtime

    @property
    def is_debug(self):
        return self.debug_port is not None

    @property
    def cmd(self):
        if self.debug_port is None:
            return self.DEBUG_CMD[self.runtime]
        return None

    @property
    def argv(self):
        if self.debug_port is None:
            return []
        argv = []
        if self.debug_argv:
            argv.append(self.debug_argv)
        if self.runtime not in self.DEBUG_CMD.keys():
            raise InvalidOptionValue("Invalid runtime. [{}] support debug".format(",".join(self.DEBUG_CMD.keys())))

        if self.runtime == MacroRuntime.node610:
            argv += self.debug_arg_node610
        elif self.runtime == MacroRuntime.node89:
            argv += self.debug_arg_node89
        elif self.runtime == MacroRuntime.python36:
            argv += self.debug_arg_python36
        elif self.runtime == MacroRuntime.python27:
            argv += self.debug_arg_python27
        else:
            pass
        return argv

    @property
    def debug_arg_node610(self):
        return [
            "--inspect",
            "--debug-brk=" + str(self.debug_port),
            "--nolazy",
            "--max-old-space-size=2547",
            "--max-semi-space-size=150",
            "--expose-gc",
        ]

    @property
    def debug_arg_node89(self):
        return [
            "--inspect-brk=0.0.0.0:" + str(self.debug_port),
            "--nolazy",
            "--expose-gc",
            "--max-semi-space-size=150",
            "--max-old-space-size=2707",
        ]
    
    @property
    def debug_arg_python36(self):
        return [
            "-m",
            "ptvsd",
            "--host",
            "0.0.0.0",
            "--port",
            str(self.debug_port),
            "--wait"
        ]
    
    @property
    def debug_arg_python27(self):
        return [
            "-m",
            "ptvsd",
            "--host",
            "0.0.0.0",
            "--port",
            str(self.debug_port),
            "--wait"
        ]