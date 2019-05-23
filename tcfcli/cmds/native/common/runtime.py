from tcfcli.libs.tcsam.model import *
from tcfcli.common.user_exceptions import InvalidTemplateException
from tcfcli.common.macro import MacroRuntime

class Runtime(object):
    RUNTIME = {
        MacroRuntime.node610: MacroRuntime.cmd_node610,
        MacroRuntime.node89: MacroRuntime.cmd_node89,
        MacroRuntime.python36: MacroRuntime.cmd_python36,
        MacroRuntime.python27: MacroRuntime.cmd_python27,
    }

    def __init__(self, proper):
        self.codeuri = proper.get(CODE_URI)
        self.env = proper.get(ENVIRONMENT, {VARIABLE: {}}).get(VARIABLE, {})
        self.handler = proper.get(HANDLER, "")
        self.mem_size = proper.get(MEMORY_SIZE, 128)
        self.runtime = proper.get(RUNTIME, "").lower()
        self.timeout = proper.get(TIMEOUT, 3)

        if self.runtime not in self.RUNTIME.keys():
            raise InvalidTemplateException("Invalid runtime. supports [{}]".
                                           format(",".join(self.RUNTIME.keys())))

    @property
    def cmd(self):
        return self.RUNTIME[self.runtime]
