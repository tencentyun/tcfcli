import click
from tcfcli.libs.function.context import Context
from tcfcli.common.user_exceptions import TemplateNotFoundException, InvalidTemplateException
from tcfcli.libs.utils.scf_client import ScfClient


@click.command()
@click.option('--template-file', '-t', type=click.Path(exists=True), help="TCF template file for deploy")
def deploy(template_file):
    '''
    Deploy a scf.
    '''
    Deploy.check_params(template_file)

    try:
        with Context(template_file=template_file) as deploy_ctx:
            Deploy(deploy_ctx).do_deploy()
    except InvalidTemplateException as e:
        raise e


class Deploy(object):
    def __init__(self, deploy_ctx):
        self._deploy_ctx = deploy_ctx

    def do_deploy(self):
        for func in self._deploy_ctx.get_functions():
            self._do_deploy_core(func)

    @staticmethod
    def check_params(template_file):
        if not template_file:
            click.secho("FAM Template Not Found", fg="red")
            raise TemplateNotFoundException("Missing option --template-file".format(template_file))

    @staticmethod
    def _do_deploy_core(func):
        """
        :param func: Function namedtuple containing the function information.
                     Example: Function = namedtuple("Function", [
                                                    "name",
                                                    "runtime",
                                                    "memory",
                                                    "timeout",
                                                    "handler",
                                                    "codeuri",
                                                    "environment",
                                                    "vpc",
                                                ])
        """
        err = ScfClient().deploy(func)
        if err is not None:
            click.secho("Deploy  function '{}' failure. Error: {}.".format(func.name,
                                                            err.get_message().encode("UTF-8")), fg="red")
            if err.get_request_id():
                click.secho("RequestId: {}".format(err.get_request_id().encode("UTF-8")), fg="red")
        else:
            click.secho("Deploy  function '{}' success".format(func.name), fg="green")
