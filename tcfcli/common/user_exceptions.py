import click


class UserException(click.ClickException):
    exit_code = 1


class InvokeContextException(UserException):
    pass


class TemplateNotFoundException(UserException):
    pass


class OutTemplateAlreadyExist(UserException):
    pass


class ContextException(UserException):
    pass


class NoApiDefinition(UserException):
    pass

class InvalidTemplateException(UserException):
    pass


class UploadToCosFailed(UserException):
    pass


class FunctionNotFound(UserException):
    pass


class InvalidCodeDirs(UserException):
    pass


class UserConfigException(UserException):
    pass


class InvalidEnvParameters(UserException):
    pass


class InvalidResourceException(Exception):
    pass


class InvalidEventException(Exception):
    pass


class InvalidDocumentException(Exception):
    def __init__(self, causes):
        self._causes = sorted(causes)

    @property
    def message(self):
        return "Invalid Specification Document. Number of errors found: {}.".format(len(self.causes))

    @property
    def causes(self):
        return self._causes
