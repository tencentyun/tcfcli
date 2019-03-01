import click
import os


_DEAFULT_TEMPLATE_FILE = 'template.[yaml|yml]'


def get_template_abspath(ctx, param, template_name):
    if template_name == _DEAFULT_TEMPLATE_FILE:
        template_name = 'template.yaml'

        tmp = 'template.yml'
        if os.path.exists(tmp):
            template_name = tmp

    return os.path.abspath(template_name)


def template_click_option():
    """
    Click Option for template option
    """
    return click.option('--template', '-t',
                        default=_DEAFULT_TEMPLATE_FILE,
                        type=click.Path(exists=True),
                        envvar="TCF_TEMPLATE_FILE",
                        callback=get_template_abspath,
                        show_default=True)


def invoke_common_options(f):
    invoke_options = [
        template_click_option(),

        click.option('--env-vars', '-n',
                     help='JSON file contains function environment variables.',
                     type=click.Path(exists=True)),

        click.option('--debug-port', '-d',
                     help='The port exposed for debugging. If specified, local container will start with debug mode.',
                     envvar="TCF_DEBUG_PORT"),

        click.option('--debugger-path',
                     help='The debugger path in host. If specified, the debugger will mounted into the function container.'),

        click.option('--debug-args',
                     help='Additional args to be passed the debugger.',
                     envvar="DEBUGGER_ARGS"),

        click.option('--docker-volume-basedir', '-v',
                     help='The basedir where TCF template locate in.',
                     envvar="TCF_DOCKER_VOLUME_BASEDIR"),

        click.option('--docker-network',
                     help='Specifies the name or id of an existing docker network which containers should connect to, '
                          'along with the default bridge network.',
                     envvar="TCF_DOCKER_NETWORK"),

        click.option('--log-file', '-l',
                     help='Path of logfile where send runtime logs to'),

        click.option('--skip-pull-image',
                     is_flag=True,
                     help='Specify whether CLI skip pulling or update docker images',
                     envvar="TCF_SKIP_PULL_IMAGE"),

        click.option('--region'),

    ]

    for option in reversed(invoke_options):
        option(f)

    return f


def service_common_options(port):
    def construct_options(f):
        service_options = [
            click.option('--host',
                         default="127.0.0.1",
                         help="Local hostname or IP address bind to (default: '127.0.0.1')"),
            click.option("--port", "-p",
                         default=port,
                         help="Local port number to listen on (default: '{}')".format(str(port)))
        ]

        for option in reversed(service_options):
            option(f)

        return f
    return construct_options