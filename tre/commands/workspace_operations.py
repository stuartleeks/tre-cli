import logging
import click
from tre.api_client import ApiClient

from .workspace_contexts import WorkspaceContext, pass_workspace_context


@click.group(name="operations", help="List operations ")
def workspace_operations():
    pass


@click.command(name="list", help="List workspace operations")
@pass_workspace_context
def workspace_operations_list(workspace_context: WorkspaceContext):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    client = ApiClient.get_api_client_from_config()

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/operations',
    )
    click.echo(response.text + '\n')


workspace_operations.add_command(workspace_operations_list)
