import click
from tcfcli.cmds.local.generate_event.events_metadata import EVENTS_METADATA
from tcfcli.cmds.local.generate_event.generate_event_action import GenerateEventAction


class GenerateEventService(click.MultiCommand):
    '''
    this is a test
    '''

    def get_command(self, ctx, cmd):
        if cmd not in EVENTS_METADATA:
            return None
        return GenerateEventAction(cmd, EVENTS_METADATA[cmd])

    def list_commands(self, ctx):
        return sorted(EVENTS_METADATA.keys())
