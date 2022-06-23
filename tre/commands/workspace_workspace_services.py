import logging
import click

from tre.api_client import ApiClient
from .workspace_contexts import pass_workspace_context


@click.group(name="workspace-services", help="List workspace-services ")
def workspace_workspace_services():
    pass


@click.command(name="list", help="List workspace services")
@pass_workspace_context
def workspace_workspace_services_list(workspace_context):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    client = ApiClient.get_api_client_from_config()

    workspace_response = client.call_api(
        log,
        "GET",
        f'/api/workspaces/{workspace_id}',
    )
    workspace_json = workspace_response.json()
    workspace_scope = workspace_json["workspace"]["properties"]["scope_id"]

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/workspace-services',
        scope_id=workspace_scope,
    )
    click.echo(response.text + '\n')


workspace_workspace_services.add_command(workspace_workspace_services_list)
