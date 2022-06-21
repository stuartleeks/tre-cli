import logging
from cliff.command import Command
from tre.api_client import ApiClient

class WorkspaceList(Command):
    "List workspaces"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        client = ApiClient.get_api_client_from_config()
        response = client.call_api(self.log, '/api/workspaces')
        self.app.stdout.write(response.text + '\n')

class WorkspaceShow(Command):
    "Show a workspace"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(WorkspaceShow, self).get_parser(prog_name)
        # Base args
        parser.add_argument(
            '--workspace-id', nargs='?',
            help='The ID of the workspace to show',
            required=True)

        return parser

    def take_action(self, parsed_args):
        client = ApiClient.get_api_client_from_config()
        response = client.call_api(self.log, f'/api/workspaces/{parsed_args.workspace_id}')
        # TODO - handle not found
        self.app.stdout.write(response.text + '\n')
