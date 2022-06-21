import logging
import click
from tre.api_client import ApiClient

from .workspace_workspace_service import workspace_workspace_service
from .workspace_operation import workspace_operation


@click.group()
def workspace(help="query workspaces"):
    pass


@click.command(name="list", help="List workspaces")
def workspace_list():
    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, '/api/workspaces')
    click.echo(response.text + '\n')


@click.command(name="show", help="Show a workspace")
@click.option('--workspace-id',
              help='The ID of the workspace to show',
              required=True)
def workspace_show(workspace_id):
    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, f'/api/workspaces/{workspace_id}')
    # TODO - handle not found
    click.echo(response.text + '\n')


workspace.add_command(workspace_list)
workspace.add_command(workspace_show)
workspace.add_command(workspace_workspace_service)
workspace.add_command(workspace_operation)
