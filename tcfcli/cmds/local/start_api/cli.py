import click
from tcfcli.cmds.local.common.options import invoke_common_options, service_common_options
from tcfcli.cmds.local.common.invoke_context import InvokeContext
from tcfcli.cmds.local.libs.apigw.api_service import LocalApiService


@click.command(short_help='Set up a local service to simulate invoke by API event')
@service_common_options(3000)
@click.option("--static-dir", "-s",
              default="public",
              help="Any static assets (e.g. CSS/Javascript/HTML) files located in this directory "
                   "will be presented at /")
@invoke_common_options
def start_api(host, port, static_dir, template, env_vars, debug_port, debug_args, debugger_path,
              docker_volume_basedir, docker_network, log_file, skip_pull_image, region):

    do_start_api(host, port, static_dir, template, env_vars, debug_port, debug_args, debugger_path,
                 docker_volume_basedir, docker_network, log_file, skip_pull_image, region)


def do_start_api(host, port, static_dir, template, env_vars, debug_port, debug_args, debugger_path,
                 docker_volume_basedir, docker_network, log_file, skip_pull_image, region):

    with InvokeContext(template_file=template,
                       function_identifier=None,
                       env_vars_file=env_vars,
                       debug_port=debug_port,
                       debug_args=debug_args,
                       debugger_path=debugger_path,
                       docker_volume_basedir=docker_volume_basedir,
                       docker_network=docker_network,
                       log_file=log_file,
                       skip_pull_image=skip_pull_image,
                       region=region) as context:

        LocalApiService(invoke_context=context, port=port, host=host, static_dir=static_dir).start()
