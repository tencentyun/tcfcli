class FunctionConfig(object):
    _DEFAULT_TIMOUT_SECONDS = 3
    _DEFAULT_MEMORY = 128

    def __init__(self,
                 name,
                 runtime,
                 handler,
                 code_uri,
                 memory=None,
                 timeout=None,
                 envs=None,
                 vpc=None):
        self.name = name
        self.runtime = runtime
        self.handler = handler
        self.code_uri = code_uri
        self.memory = memory or self._DEFAULT_MEMORY
        self.timeout = timeout or self._DEFAULT_TIMOUT_SECONDS

        if not envs:
            # future set default
            pass

        if not vpc:
            pass


class EnviromentVariables(object):
    pass


class VpcConfigs(object):
    pass
