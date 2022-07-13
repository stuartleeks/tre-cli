import click
import logging

from tre.api_client import ApiClient
from .workspace_contexts import pass_workspace_context, WorkspaceContext

from .workspace_workspace_service import workspace_workspace_service
from .workspace_workspace_services import workspace_workspace_services
from .workspace_operation import WorkspaceOperationContext, workspace_operation_show, workspace_operation
from .workspace_operations import workspace_operations


@click.group(invoke_without_command=True, help="Perform actions on an individual workspace")
@click.argument('workspace_id', envvar='TRECLI_WORKSPACE_ID', required=True)
@click.pass_context
def workspace(ctx: click.Context, workspace_id: str) -> None:
    ctx.obj = WorkspaceContext(workspace_id)


@click.command(name="show", help="Show a workspace")
@pass_workspace_context
def workspace_show(workspace_context: WorkspaceContext):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', f'/api/workspaces/{workspace_id}', )
    click.echo(response.text + '\n')


@click.command(name="set-enabled", help="Enable/disable a workspace")
@click.option('--etag',
              help='The etag of the workspace to update',
              required=True)
@click.option('--enable/--disable', is_flag=True, required=True)
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
@pass_workspace_context
def workspace_set_enabled(workspace_context: WorkspaceContext, ctx: click.Context, etag, enable, wait_for_completion, suppress_output: bool = False):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    client = ApiClient.get_api_client_from_config()
    click.echo(f"Setting isEnabled to {enable}...", err=True)
    response = client.call_api(
        log,
        'PATCH',
        f'/api/workspaces/{workspace_id}',
        headers={'etag': etag},
        json_data={'isEnabled': enable})
    if wait_for_completion:
        ctx.obj = WorkspaceOperationContext.from_operation_response(response)
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(workspace_operation_show, wait_for_completion=True, suppress_output=suppress_output)
    else:
        if not suppress_output:
            click.echo(response.text + '\n')


@click.command(name="delete", help="Delete a workspace")
@click.option('--yes', is_flag=True, default=False)
@click.option('--wait-for-completion',
              flag_value=True,
              help="Wait for the operation to complete if it is in progress",
              default=False)
@click.option('--ensure-disabled',
              help="Disable before deleting if not currently enabled",
              flag_value=True,
              default=False)
@ click.pass_context
@ pass_workspace_context
def workspace_delete(workspace_context: WorkspaceContext, ctx: click.Context, yes, wait_for_completion, ensure_disabled):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    if not yes:
        click.confirm("Are you sure you want to delete this workspace?", err=True, abort=True)

    client = ApiClient.get_api_client_from_config()

    if ensure_disabled:
        response = client.call_api(log, 'GET', f'/api/workspaces/{workspace_id}')
        workspace_json = response.json()
        if workspace_json['workspace']['isEnabled']:
            etag = workspace_json['workspace']['_etag']
            ctx.invoke(
                workspace_set_enabled,
                etag=etag,
                enable=False,
                wait_for_completion=True,
                suppress_output=True
            )

    click.echo("Deleting workspace...", err=True)
    response = client.call_api(log, 'DELETE', f'/api/workspaces/{workspace_id}')
    if wait_for_completion:
        ctx.obj = WorkspaceOperationContext.from_operation_response(response)
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(workspace_operation_show, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


workspace.add_command(workspace_show)
workspace.add_command(workspace_set_enabled)
workspace.add_command(workspace_delete)
workspace.add_command(workspace_workspace_services)
workspace.add_command(workspace_workspace_service)
workspace.add_command(workspace_operations)
workspace.add_command(workspace_operation)
