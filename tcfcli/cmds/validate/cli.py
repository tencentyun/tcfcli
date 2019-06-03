import click
from tcfcli.common import tcsam
from tcfcli.common.template import Template

@click.command(name="validate")
@click.option('--template-file', '-t', type=click.Path(exists=True), help="TCF template file for deploy")
def validate(template_file):
    '''
    validate a scf template.
    '''
    tcsam.tcsam_validate(Template.get_template_data(template_file))