import logging
from cliff.command import Command
from tre.api_client import ApiClient


class WorkspaceWorkspaceServiceList(Command):
    "List workspaces"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(WorkspaceWorkspaceServiceList,
                       self).get_parser(prog_name)
        parser.add_argument(
            '--workspace-id', nargs='?',
            help='The ID of the workspace to list workspace services for',
            required=True)

        return parser

    def take_action(self, parsed_args):
        client = ApiClient.get_api_client_from_config()
        workspace_response = client.call_api(
            self.log, f'/api/workspaces/{parsed_args.workspace_id}')
        # TODO - handle not found
        workspace_json = workspace_response.json()
        workspace_scope = workspace_json["workspace"]["properties"]["scope_id"]

        response = client.call_api(
            self.log, f'/api/workspaces/{parsed_args.workspace_id}/workspace-services', workspace_scope)
        self.app.stdout.write(response.text + '\n')
