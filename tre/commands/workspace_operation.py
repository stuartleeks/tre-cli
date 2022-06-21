import logging
from cliff.command import Command
from tre.api_client import ApiClient


class WorkspaceOperationList(Command):
    "List workspaces"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(WorkspaceOperationList, self).get_parser(prog_name)
        parser.add_argument(
            '--workspace-id', nargs='?',
            help='The ID of the workspace to list operations for',
            required=True)

        return parser

    def take_action(self, parsed_args):
        client = ApiClient.get_api_client_from_config()
        response = client.call_api(
            self.log, f'/api/workspaces/{parsed_args.workspace_id}/operations')
        self.app.stdout.write(response.text + '\n')


class WorkspaceOperationShow(Command):
    "Show a workspace"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(WorkspaceOperationShow, self).get_parser(prog_name)
        parser.add_argument(
            '--workspace-id', nargs='?',
            help='The ID of the workspace to show',
            required=True)
        parser.add_argument(
            '--operation-id', nargs='?',
            help='The ID of the operation to show',
            required=True)

        return parser

    def take_action(self, parsed_args):
        client = ApiClient.get_api_client_from_config()
        response = client.call_api(
            self.log, f'/api/workspaces/{parsed_args.workspace_id}/operations/{parsed_args.operation_id}')
        # TODO - handle not found
        self.app.stdout.write(response.text + '\n')
