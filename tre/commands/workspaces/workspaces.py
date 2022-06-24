import click
import json
import logging

from tre.api_client import ApiClient

from .workspace_contexts import WorkspaceOperationContext
from .workspace_operation import workspace_operation_show


@click.group(help="List/add workspaces")
def workspaces() -> None:
    pass


@click.command(name="list", help="List workspaces")
def workspaces_list():
    log = logging.getLogger(__name__)

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', '/api/workspaces')
    click.echo(response.text + '\n')


@click.command(name="new", help="Create a new workspace")
@click.option('--definition', help='JSON definition for the workspace', required=False)
@click.option('--definition-file', help='File containing JSON definition for the workspace', required=False, type=click.File("r"))
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
def workspaces_create(ctx, definition, definition_file, wait_for_completion):
    log = logging.getLogger(__name__)

    if definition is None:
        if definition_file is None:
            raise click.UsageError('Please specify either a definition or a definition file')
        definition = definition_file.read()

    definition_dict = json.loads(definition)

    client = ApiClient.get_api_client_from_config()
    click.echo("Creating workspace...", err=True)
    response = client.call_api(log, 'POST', '/api/workspaces', json=definition_dict)

    if wait_for_completion:
        ctx.obj = WorkspaceOperationContext.from_operation_response(response)
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(workspace_operation_show, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


@click.group(invoke_without_command=True, help="Perform actions on an individual workspace")
@click.argument('workspace_id', envvar='TRECLI_WORKSPACE_ID', required=True)
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
    click.echo(f"Setting isEnabled to {enable}...\n", err=True)
    response = client.call_api(
        log,
        'PATCH',
        f'/api/workspaces/{workspace_id}',
        verify,
        headers={'etag': etag},
        json={'isEnabled': enable})
    if wait_for_completion:
        response_json = response.json()
        ctx.obj['workspace_id'] = response_json['operation']['resourceId']
        ctx.obj['operation_id'] = response_json['operation']['id']
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(workspace_operation_show, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


@click.command(name="delete", help="Delete a workspace")
@click.option('--yes', is_flag=True, default=False)
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
def workspace_delete(ctx, yes, wait_for_completion):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    workspace_id = obj['workspace_id']
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    verify = obj['verify']

    if not yes:
        click.confirm("Are you sure you want to delete this workspace?", err=True, abort=True)

    client = ApiClient.get_api_client_from_config()
    click.echo("Deleting workspace...\n", err=True)
    response = client.call_api(log, 'DELETE', f'/api/workspaces/{workspace_id}', verify)
    if wait_for_completion:
        response_json = response.json()
        ctx.obj['operation_id'] = response_json['operation']['id']
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(workspace_operation_show, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


workspaces.add_command(workspaces_list)
workspaces.add_command(workspaces_create)
