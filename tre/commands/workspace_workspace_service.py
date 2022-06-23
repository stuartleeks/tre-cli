import logging
import click
from tre.api_client import ApiClient


@click.group(name="workspace-services", invoke_without_command=True, help="List workspace-services ")
@click.pass_context
def workspace_workspace_services(ctx: click.Context) -> None:
    pass


@click.group(name="workspace-service", invoke_without_command=True, help="Perform actions on an workspace-service")
@click.argument('service_id', required=True)
@click.pass_context
def workspace_workspace_service(ctx: click.Context, service_id) -> None:
    ctx.obj["service_id"] = service_id


@click.command(name="list", help="List workspace services")
@click.pass_context
def workspace_workspace_services_list(ctx):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    workspace_id = obj['workspace_id']
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()

    workspace_response = client.call_api(
        log,
        "GET",
        f'/api/workspaces/{workspace_id}',
        verify
    )
    workspace_json = workspace_response.json()
    workspace_scope = workspace_json["workspace"]["properties"]["scope_id"]

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/workspace-services',
        verify,
        scope_id=workspace_scope,
    )
    click.echo(response.text + '\n')


@click.command(name="show", help="Workspace service")
@click.pass_context
def workspace_workspace_service_show(ctx):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    workspace_id = obj['workspace_id']
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    service_id = obj['service_id']
    if service_id is None:
        raise click.UsageError('Missing service ID')
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()

    workspace_response = client.call_api(
        log,
        "GET",
        f'/api/workspaces/{workspace_id}',
        verify
    )
    workspace_json = workspace_response.json()
    workspace_scope = workspace_json["workspace"]["properties"]["scope_id"]

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/workspace-services/{service_id}',
        verify,
        scope_id=workspace_scope,
    )

    click.echo(response.text + '\n')


workspace_workspace_services.add_command(workspace_workspace_services_list)

workspace_workspace_service.add_command(workspace_workspace_service_show)
