import click
import platform
from tcfcli.common.user_config import UserConfig
version = platform.python_version()
if version >= '3':
    from functools import reduce

@click.command()
@click.option('--secret-id', is_flag=True, help="TencentCloudAPI  SecretId")
@click.option('--secret-key', is_flag=True, help="TencentCloudAPI  SecretKey")
@click.option('--region', is_flag=True,  help="TencentCloudAPI  Region")
@click.option('--appid', is_flag=True, help="TencentCloudAPI  Appid")
def get(**kwargs):
    uc = UserConfig()
    def set_true(k):
        kwargs[k] = True
    bools = [v for k, v in kwargs.items()]
    if not reduce(lambda x, y: bool(x or y), bools):
        list(map(set_true, kwargs))
    attrs = uc.get_attrs(kwargs)
    msg = "{} config:\n".format(UserConfig.API)
    for attr in sorted(attrs):
         msg += "{} = {}\n".format(attr, attrs[attr])
    click.secho(msg.strip())


@click.command()
@click.option('--secret-id', help="TencentCloudAPI  SecretId")
@click.option('--secret-key', help="TencentCloudAPI  SecretKey")
@click.option('--region', help="TencentCloudAPI  Region")
@click.option('--appid', help="TencentCloudAPI  Region")
def set(**kwargs):
    uc = UserConfig()
    uc.set_attrs(kwargs)
    uc.flush()


@click.group(name='configure')
def configure():
    """
    Configure your account parameters
    """
    pass

configure.add_command(get)
configure.add_command(set)
