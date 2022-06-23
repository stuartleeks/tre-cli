import click
import json
import logging
from tre.api_client import ApiClient

from .workspace_workspace_service import workspace_workspace_services, workspace_workspace_service
from .workspace_operation import workspace_operations, workspace_operation


def confirmation_callback(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    # TODO - move to lib file?
    if not value:
        ctx.abort()


@click.group(invoke_without_command=True, help="List/add workspaces")
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)  # TODO move to top level command
@click.pass_context
def workspaces(ctx: click.Context, verify: bool) -> None:
    ctx.obj = {'verify': verify}


@click.command(name="list", help="List workspaces")
@click.pass_context
def workspaces_list(ctx: click.Context):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', '/api/workspaces', verify)
    click.echo(response.text + '\n')


@click.group(invoke_without_command=True, help="Perform actions on an individual workspace")
@click.argument('workspace_id', envvar='TRECLI_WORKSPACE_ID', required=True)
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)  # TODO move to top level command
@click.pass_context
def workspace(ctx: click.Context, workspace_id: str, verify: bool) -> None:
    ctx.obj = {'workspace_id': workspace_id, 'verify': verify}


@click.command(name="show", help="Show a workspace")
@click.pass_context
def workspace_show(ctx: click.Context):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    workspace_id = obj['workspace_id']
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', f'/api/workspaces/{workspace_id}', verify)
    click.echo(response.text + '\n')


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


@click.command(name="new", help="Create a new workspace")
@click.option('--definition', help='JSON definition for the workspace', required=False)
@click.option('--definition-file', help='File containing JSON definition for the workspace', required=False, type=click.File("r"))
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
def workspace_create(ctx, definition, definition_file, wait_for_completion):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    # TODO - look at multi command groups in docs - can we have `workspaces create` not show as needing workspace ID?
    verify = obj['verify']

    if definition is None:
        if definition_file is None:
            raise click.UsageError('Please specify either a definition or a definition file')
        definition = definition_file.read()

    definition_dict = json.loads(definition)

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'POST', '/api/workspaces', verify, json=definition_dict)

    if wait_for_completion:
        ctx.invoke(workspace_operations, operation_id=response.json()['operation']['id'], wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


workspaces.add_command(workspaces_list)
workspaces.add_command(workspace_create)

workspace.add_command(workspace_show)
workspace.add_command(workspace_set_enabled)
workspace.add_command(workspace_delete)
workspace.add_command(workspace_workspace_services)
workspace.add_command(workspace_workspace_service)
workspace.add_command(workspace_operations)
workspace.add_command(workspace_operation)
