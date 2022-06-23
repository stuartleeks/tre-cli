import logging
import click
from tre.api_client import ApiClient

from .workspace_contexts import WorkspaceWorkspaceServiceContext, pass_workspace_workspace_service_context


@click.group(name="workspace-service", invoke_without_command=True, help="Perform actions on an workspace-service")
@click.argument('service_id', required=True)
@click.pass_context
def workspace_workspace_service(ctx: click.Context, service_id) -> None:
    ctx.obj = WorkspaceWorkspaceServiceContext.add_service_id_to_context_obj(ctx, service_id)


@click.command(name="show", help="Workspace service")
@pass_workspace_workspace_service_context
def workspace_workspace_service_show(workspace_workspace_service_context: WorkspaceWorkspaceServiceContext):
    log = logging.getLogger(__name__)

    workspace_id = workspace_workspace_service_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    service_id = workspace_workspace_service_context.service_id
    if service_id is None:
        raise click.UsageError('Missing service ID')

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
        f'/api/workspaces/{workspace_id}/workspace-services/{service_id}',
        scope_id=workspace_scope,
    )

    click.echo(response.text + '\n')


workspace_workspace_service.add_command(workspace_workspace_service_show)
