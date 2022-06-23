import logging
import click
from tre.api_client import ApiClient


@click.group(name="workspace-service", help="Workspace services")
def workspace_workspace_service():
    pass


@click.command(name="list", help="List workspace services")
@click.option('--workspace-id',
              envvar='TRECLI_WORKSPACE_ID',
              help='The ID of the workspace to show workspace services for',
              required=True)
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)
def workspace_workspace_service_list(workspace_id, verify):
    log = logging.getLogger(__name__)

    client = ApiClient.get_api_client_from_config()
    workspace_response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}',
        verify)
    workspace_json = workspace_response.json()
    workspace_scope = workspace_json["workspace"]["properties"]["scope_id"]

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/workspace-services',
        workspace_scope)
    click.echo(response.text + '\n')


workspace_workspace_service.add_command(workspace_workspace_service_list)
