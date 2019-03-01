import click
from cookiecutter.main import cookiecutter
from cookiecutter import exceptions


class Init(object):

    RUNTIMES = {
        "python3.6": "gh:tencentyun/tcf-demo-python",
        "python2.7": "gh:tencentyun/tcf-demo-python",
        "go1": "gh:tencentyun/tcf-demo-go1",
        "php5": "gh:tencentyun/tcf-demo-php",
        "php7": "gh:tencentyun/tcf-demo-php",
        "nodejs6.10": "gh:tencentyun/tcf-demo-nodejs6.10",
        "nodejs8.9": "gh:tencentyun/tcf-demo-nodejs8.9",
        # "java8": "gh:tencentyun/tcf-demo-java8"
    }

    @staticmethod
    def do_cli(location, runtime, output_dir, name, no_input):

        click.secho("[+] Initializing project...", fg="green")
        params = {
            "template": location if location else Init.RUNTIMES[runtime],
            "output_dir": output_dir,
            "no_input": no_input,
        }
        click.secho("Template: %s" % params["template"])
        click.secho("Output-Dir: %s" % params["output_dir"])
        if not location and name is not None:
            params["no_input"] = True
            params['extra_context'] = {'project_name': name, 'runtime': runtime}
            click.secho("Project-Name: %s" % params['extra_context']["project_name"])
            click.secho("Runtime: %s" % params['extra_context']["runtime"])

        try:
            cookiecutter(**params)
        except exceptions.CookiecutterException as e:
            click.secho(e.message, fg="red")
            raise click.Abort()
        click.secho("[*] Project initialization is complete", fg="green")


@click.command()
@click.option('-l', '--location', help="Template location (git, mercurial, http(s), zip, path)")
@click.option('-r', '--runtime', type=click.Choice(Init.RUNTIMES.keys()), default="python3.6",
              help="Scf Runtime of your app")
@click.option('-o', '--output-dir', default='.', type=click.Path(), help="Where to output the initialized app into")
@click.option('-n', '--name',  default="demo", help="Name of your project to be generated as a folder")
@click.option('-N', '--no-input', is_flag=True, help="Disable prompting and accept default values defined template config")
def init(location, runtime, output_dir, name, no_input):
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
    Init.do_cli(location, runtime, output_dir, name, no_input)
