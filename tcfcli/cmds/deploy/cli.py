import click
import sys
from tcfcli.common.template import Template
from tcfcli.common.user_exceptions import TemplateNotFoundException, InvalidTemplateException
from tcfcli.libs.utils.scf_client import ScfClient
from tcfcli.common import tcsam
from tcfcli.common.tcsam.tcsam_macro import TcSamMacro as tsmacro


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
        template_data = tcsam.tcsam_validate(Template.get_template_data(self.template_file))
        self.resources = template_data.get(tsmacro.Resources)
        self.forced = forced

    def do_deploy(self):
        for ns in self.resources:
            if not self.resources[ns]:
                continue
            click.secho("deploy {ns} begin".format(ns=ns))
            for func in self.resources[ns]:
                if func == tsmacro.Type:
                    continue
                self._do_deploy_core(self.resources[ns][func], func, ns, self.forced)
            click.secho("deploy {ns} end".format(ns=ns))

    def check_params(self):
        if not self.template_file:
            click.secho("FAM Template Not Found", fg="red")
            raise TemplateNotFoundException("Missing option --template-file")

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
        proper = func.get(tsmacro.Properties, {})
        events = proper.get(tsmacro.Events, {})

        for trigger in events:
            err = ScfClient().deploy_trigger(events[trigger], trigger, func_name, func_ns)
            if err is not None:
                if sys.version_info[0] == 3:
                    s = err.get_message()
                else:
                    s = err.get_message().encode("UTF-8")

                click.secho(
                    "Deploy trigger '{name}' failure. Error: {e}.".format(name=trigger,
                                                            e=s), fg="red")
                if err.get_request_id():
                    click.secho("RequestId: {}".format(err.get_request_id().encode("UTF-8")), fg="red")
                continue
            click.secho("Deploy trigger '{name}' success".format(name=trigger),fg="green")

