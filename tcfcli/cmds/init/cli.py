import os
import click
from cookiecutter.main import cookiecutter
from cookiecutter import exceptions


class Init(object):

    TEMPLATES_DIR ="templates"
    RUNTIMES = {
        "python3.6": "tcf-demo-python",
        "python2.7": "tcf-demo-python",
        "go1": "tcf-demo-go1",
        "php5": "tcf-demo-php",
        "php7": "tcf-demo-php",
        "nodejs6.10": "tcf-demo-nodejs6.10",
        "nodejs8.9": "tcf-demo-nodejs8.9",
        # "java8": "gh:tencentyun/tcf-demo-java8"
    }
    @staticmethod
    def _runtime_path(runtime):
        pwd = os.path.dirname(os.path.abspath(__file__))
        runtime_pro = Init.RUNTIMES[runtime]
        return os.path.join(pwd, Init.TEMPLATES_DIR, runtime_pro)

    @staticmethod
    def do_cli(location, runtime, output_dir, name, namespace, no_input):

        click.secho("[+] Initializing project...", fg="green")
        params = {
            "template": location if location else Init._runtime_path(runtime),
            "output_dir": output_dir,
            "no_input": no_input,
        }
        click.secho("Template: %s" % params["template"])
        click.secho("Output-Dir: %s" % params["output_dir"])
        if not location and name is not None:
            params["no_input"] = True
            params['extra_context'] = {'project_name': name, 'runtime': runtime, 'namespace': namespace}
            click.secho("Project-Name: %s" % params['extra_context']["project_name"])
            click.secho("Runtime: %s" % params['extra_context']["runtime"])

        try:
            cookiecutter(**params)
        except exceptions.CookiecutterException as e:
            click.secho(str(e), fg="red")
            raise click.Abort()
        click.secho("[*] Project initialization is complete", fg="green")


@click.command()
@click.option('-l', '--location', help="Template location (git, mercurial, http(s), zip, path)")
@click.option('-r', '--runtime', type=click.Choice(Init.RUNTIMES.keys()), default="python3.6",
              help="Scf Runtime of your app")
@click.option('-o', '--output-dir', default='.', type=click.Path(), help="Where to output the initialized app into")
@click.option('-n', '--name',  default="hello_world", help="Function name")
@click.option('-ns', '--namespace',  default="default", help="Namespace name")
@click.option('-N', '--no-input', is_flag=True, help="Disable prompting and accept default values defined template config")
def init(location, runtime, output_dir, name, namespace, no_input):
    """
    \b
    Initialize a Serverless Cloud Function with a scf template

    Common usage:

        \b
        Initializes a new scf using Python 3.6 default template runtime
        \b
        $ tcf init --runtime python3.6
        \b
        Initializes a new scf project using custom template in a Git repository
        \b
        $ tcf init --location gh:pass/demo-python
    """
    Init.do_cli(location, runtime, output_dir, name, namespace, no_input)
