import click
from tcfcli.libs.tcsam.tcsam import Resources
from tcfcli.libs.function.context import Context
from tcfcli.common import tcsam

@click.command(name="validate")
@click.option('--template-file', '-t', type=click.Path(exists=True), help="TCF template file for deploy")
def validate(template_file):
    '''
    validate a scf template.
    '''
    ret = tcsam.tcsam_validate(Context.get_template_data(template_file))
    if ret:
        click.secho("Invalid:{}".format(ret), fg="red")
    # resource = Resources(Context.get_template_data(template_file))