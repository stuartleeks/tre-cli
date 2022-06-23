import logging
import click
from tre.api_client import ApiClient

from .workspace_workspace_service import workspace_workspace_service
from .workspace_operation import workspace_operations


@click.group(invoke_without_command=True, help="Workspace commands")
@click.argument('workspace_id', envvar='TRECLI_WORKSPACE_ID', required=False)
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)
@click.pass_context
def workspaces(ctx: click.Context, workspace_id: str, verify: bool) -> None:
    if ctx.invoked_subcommand is None:
        log = logging.getLogger(__name__)
        client = ApiClient.get_api_client_from_config()
        if workspace_id is None:
            # list
            response = client.call_api(log, 'GET', '/api/workspaces', verify)
            click.echo(response.text + '\n')
        else:
            # show
            response = client.call_api(log, 'GET', f'/api/workspaces/{workspace_id}', verify)
            click.echo(response.text + '\n')
    else:
        ctx.obj = {'workspace_id': workspace_id, 'verify': verify}


def confirmation_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    if not value:
        ctx.abort()


@click.command(name="set-enabled", help="Delete a workspace")
@click.option('--etag',
              help='The etag of the workspace to update',
              required=True)
@click.option('--enable/--disable', is_flag=True, required=True)
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
def workspace_set_enabled(ctx, etag, enable, wait_for_completion):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    workspace_id = obj['workspace_id']
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(
        log,
        'PATCH',
        f'/api/workspaces/{workspace_id}',
        verify,
        headers={'etag': etag},
        json={'isEnabled': enable})
    if wait_for_completion:
        ctx.invoke(workspace_operations, operation_id=response.json()['operation']['id'], wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


@click.command(name="delete", help="Delete a workspace")
@click.option('--yes', is_flag=True, default=False)
@click.pass_context
def workspace_delete(ctx, yes):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    workspace_id = obj['workspace_id']
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    verify = obj['verify']

    if not yes:
        click.confirm("Are you sure you want to delete this workspace?", err=True, abort=True)

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'DELETE', f'/api/workspaces/{workspace_id}', verify)
    click.echo(response.text + '\n')


workspaces.add_command(workspace_set_enabled)
workspaces.add_command(workspace_delete)
workspaces.add_command(workspace_workspace_service)
workspaces.add_command(workspace_operations)
