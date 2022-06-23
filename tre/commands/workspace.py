import logging
from multiprocessing.connection import wait
import click
from tre.api_client import ApiClient

from .workspace_workspace_service import workspace_workspace_service
from .workspace_operation import workspace_operation, workspace_operation_show


@click.group()
def workspace(help="query workspaces"):
    pass


@click.command(name="list", help="List workspaces")
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)
def workspace_list(verify):
    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', '/api/workspaces', verify)
    click.echo(response.text + '\n')


@click.command(name="show", help="Show a workspace")
@click.option('--workspace-id',
              envvar='TRECLI_WORKSPACE_ID',
              help='The ID of the workspace to show',
              required=True)
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)
def workspace_show(workspace_id, verify):
    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', f'/api/workspaces/{workspace_id}', verify)
    click.echo(response.text + '\n')


def confirmation_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    if not value:
        ctx.abort()


@click.command(name="set-enabled", help="Delete a workspace")
@click.option('--workspace-id',
              envvar='TRECLI_WORKSPACE_ID',
              help='The ID of the workspace to update',
              required=True)
@click.option('--etag',
              help='The etag of the workspace to update',
              required=True)
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True,
              )
@click.option('--enable/--disable', is_flag=True, required=True)
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
def workspace_set_enabled(ctx, workspace_id, etag, verify, enable, wait_for_completion):
    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(
        log,
        'PATCH',
        f'/api/workspaces/{workspace_id}',
        verify,
        headers={'etag': etag},
        json={'isEnabled': enable})
    if wait_for_completion:
        ctx.invoke(workspace_operation_show, workspace_id=workspace_id, operation_id=response.json()['operation']['id'], verify=verify, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


@click.command(name="delete", help="Delete a workspace")
@click.option('--workspace-id',
              envvar='TRECLI_WORKSPACE_ID',
              help='The ID of the workspace to show',
              required=True)
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True,
              )
@click.option('--yes', is_flag=True, default=False)
def workspace_delete(workspace_id, verify, yes):
    log = logging.getLogger(__name__)
    if not yes:
        click.confirm("Are you sure you want to delete this workspace?", err=True, abort=True)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'DELETE', f'/api/workspaces/{workspace_id}', verify)
    click.echo(response.text + '\n')


workspace.add_command(workspace_list)
workspace.add_command(workspace_show)
workspace.add_command(workspace_set_enabled)
workspace.add_command(workspace_delete)
workspace.add_command(workspace_workspace_service)
workspace.add_command(workspace_operation)
