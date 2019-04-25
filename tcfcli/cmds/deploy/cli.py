import click
import sys
from tcfcli.libs.function.context import Context
from tcfcli.common.user_exceptions import TemplateNotFoundException, InvalidTemplateException
from tcfcli.libs.utils.scf_client import ScfClient
from tcfcli.libs.tcsam.tcsam import Resources


@click.command()
@click.option('--template-file', '-t', type=click.Path(exists=True), help="TCF template file for deploy")
@click.option('-f', '--forced', is_flag=True, default=False,
              help="Update the function when it already exists,default false")
def deploy(template_file, forced):
    '''
    Deploy a scf.
    '''
    deploy = Deploy(template_file, forced)
    deploy.do_deploy()


class Deploy(object):
    def __init__(self, template_file, forced=False):
        self.template_file = template_file
        self.check_params()
        self.resource = Resources(Context.get_template_data(self.template_file))
        self.forced = forced

    def do_deploy(self):
        for ns_name, ns in vars(self.resource).items():
            click.secho("deploy {ns} begin".format(ns=ns_name))
            for func_name, func in vars(ns).items():
                self._do_deploy_core(func, func_name, ns_name, self.forced)
            click.secho("deploy {ns} end".format(ns=ns_name))

    def check_params(self):
        if not self.template_file:
            click.secho("FAM Template Not Found", fg="red")
            raise TemplateNotFoundException("Missing option --template-file".format(self.template_file))

    def _do_deploy_core(self, func, func_name, func_ns, forced):
        err = ScfClient().deploy_func(func, func_name, func_ns, forced)
        if err is not None:
            if sys.version_info[0] == 3:
                s = err.get_message()
            else:
                s = err.get_message().encode("UTF-8")
            click.secho("Deploy function '{name}' failure. Error: {e}.".format(name=func_name,
                                                            e=s), fg="red")
            if err.get_request_id():
                click.secho("RequestId: {}".format(err.get_request_id().encode("UTF-8")), fg="red")
            return

        click.secho("Deploy function '{name}' success".format(name=func_name), fg="green")
        self._do_deploy_trigger(func, func_name, func_ns)

    def _do_deploy_trigger(self, func, func_name, func_ns):
        events = getattr(func, "Events", None)
        if events is None:
            return
        for name, trigger in vars(events).items():
            err = ScfClient().deploy_trigger(trigger, name, func_name, func_ns)
            if err is not None:
                if sys.version_info[0] == 3:
                    s = err.get_message()
                else:
                    s = err.get_message().encode("UTF-8")

                click.secho(
                    "Deploy trigger '{name}' failure. Error: {e}.".format(name=name,
                                                            e=s), fg="red")
                if err.get_request_id():
                    click.secho("RequestId: {}".format(err.get_request_id().encode("UTF-8")), fg="red")
                continue
            click.secho("Deploy trigger '{name}' success".format(name=name),fg="green")

