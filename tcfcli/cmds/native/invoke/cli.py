import click
from tcfcli.cmds.native.common.invoke_context import InvokeContext
from tcfcli.cmds.local.common.options import invoke_common_options
from tcfcli.common.user_exceptions import UserException

DEF_TMP_FILENAME = "template.yaml"

STD_IN = '-'


@click.command(name='invoke')
@click.option('--event', '-e', type=click.Path(), default=STD_IN)
@click.option('--no-event', is_flag=True, default=False)
@click.option('--env-vars', '-n', help='JSON file contains function environment variables.', type=click.Path(exists=True))
@click.option('--template', '-t', default=DEF_TMP_FILENAME, type=click.Path(exists=True),
              envvar="TCF_TEMPLATE_FILE", show_default=True)
@click.option('--debug-port', '-d', help='The port exposed for debugging.', default=None)
@click.option('--debug-args', help='Additional args to be passed the debugger.', default="")
@click.argument('namespace_identifier', required=False)
@click.argument('function_identifier', required=False)
def invoke(template, namespace_identifier, function_identifier, env_vars, event, no_event, debug_port, debug_args):
    '''
    \b
    Execute your scf in a environment natively
    \b
    Common usage:
        \b
        $ tcf native invoke -t template.yaml
    '''
    do_invoke(template, namespace_identifier, function_identifier, env_vars, event, no_event, debug_port, debug_args)


def do_invoke(template, namespace, function, env_vars, event, no_event, debug_port, debug_args):

    if no_event:
        event_data = "{}"
    else:
        click.secho('Enter a event:', color="green")
        with click.open_file(event, 'r') as f:
            event_data = f.read()
    try:
        with InvokeContext(
            template_file=template,
            namespace=namespace,
            function=function,
            env_file=env_vars,
            debug_port=debug_port,
            debug_args=debug_args,
            event=event_data
        ) as context:
            context.invoke()
    except Exception as e:
        raise e


def _get_event(event_file):
    if event_file == STD_IN:
        click.secho('read event from stdin')

    with click.open_file(event_file, 'r') as f:
        return f.read()
