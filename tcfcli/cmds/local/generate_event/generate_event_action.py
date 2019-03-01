import click
import base64
import os
import json
from tcfcli.libs.utils import py_version
from chevron import renderer


class GenerateEventAction(click.MultiCommand):
    '''
    this is a test
    '''

    PARAMS = "params"

    def __init__(self, service, srv_info, *args, **kwargs):
        super(GenerateEventAction, self).__init__(*args, **kwargs)
        self.service = service
        self.srv_info = srv_info

    def get_command(self, ctx, cmd):

        if cmd not in self.srv_info:
            return None

        params = []
        for param in self.srv_info[cmd][self.PARAMS].keys():
            default = self.srv_info[cmd][self.PARAMS][param]["default"]
            params.append(click.Option(
                ["--{}".format(param)],
                default=default,
                help="Specify the {}, default is {}".format(param, default)
            ))

        cbfun = click.pass_context(self.action)
        cmd = click.Command(name=cmd,
                            short_help=self.srv_info[cmd]["help"],
                            params=params, callback=cbfun)

        return cmd

    def list_commands(self, ctx):
        return sorted(self.srv_info)

    def action(self, ctx, *args, **params):
        action = ctx.info_name
        params_tmp = self.srv_info[action][self.PARAMS]

        params = self._param_encode(params,  params_tmp)

        pwd = os.path.dirname(os.path.abspath(__file__))
        filename = self.srv_info[action]["filename"] + ".js"
        path = os.path.join(pwd, "events", self.service, filename)

        with open(path) as f:
            data = f.read().strip()

        data = renderer.render(data, params)
        click.secho(json.dumps(json.loads(data), indent=2))

    def _param_encode(self, params, param_tmp):
        for p in params:
            encoding = param_tmp[p].get("encoding")
            if encoding == "url":
                params[p] = py_version.url_encoding(params[p])
            elif encoding == "base64":
                params[p] = base64.b64encode(params[p].encode('utf8')).decode('utf-8')
        return params
