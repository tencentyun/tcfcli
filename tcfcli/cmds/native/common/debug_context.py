from tcfcli.common.user_exceptions import InvalidOptionValue
from tcfcli.common import macro


class DebugContext(object):

    DEBUG_CMD = {
        macro.RUNTIME_NODEJS_610: macro.CMD_NODE,
        macro.RUNTIME_NODEJS_89: macro.CMD_NODE
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

        if self.runtime == macro.RUNTIME_NODEJS_610:
            argv += self.debug_arg_node610
        elif self.runtime == macro.RUNTIME_NODEJS_89:
            argv += self.debug_arg_node89
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