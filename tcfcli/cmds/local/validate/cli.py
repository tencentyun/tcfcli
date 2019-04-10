import click
from tcfcli.libs.tcsam.tcsam import Resources
from tcfcli.libs.function.context import Context


@click.command(name="validate")
@click.option('--template-file', '-t', type=click.Path(exists=True), help="TCF template file for deploy")
def validate(template_file):
    '''
    validate a scf template.
    '''
    resource = Resources(Context.get_template_data(template_file))