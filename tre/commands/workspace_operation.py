import logging
import click
from tre.api_client import ApiClient


@click.group(name="operation", help="Workspace operations")
def workspace_operation():
    pass


@click.command(name="list", help="List operations")
@click.option('--workspace-id',
              help='The ID of the workspace to show operations for',
              required=True)
def workspace_operation_list(workspace_id):
    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(
        log,  f'/api/workspaces/{workspace_id}/operations')
    click.echo(response.text + '\n')


@click.command(name="show", help="Show an operation")
@click.option('--workspace-id',
              help='The ID of the workspace to show operation for',
              required=True)
@click.option('--operation-id',
              help='The ID of the operation to show',
              required=True)
def workspace_operation_show(workspace_id, operation_id):
    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(
        log, f'/api/workspaces/{workspace_id}/operations/{operation_id}')
    # TODO - handle not found
    click.echo(response.text + '\n')

workspace_operation.add_command(workspace_operation_list)
workspace_operation.add_command(workspace_operation_show)