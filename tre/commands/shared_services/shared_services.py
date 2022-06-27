import click
import json
import logging

from tre.api_client import ApiClient

from .shared_service_contexts import SharedServiceOperationContext
from .shared_service_operation import shared_service_operation_show


@click.group(help="List/add shared_services")
def shared_services() -> None:
    pass


@click.command(name="list", help="List shared_services")
def shared_services_list():
    log = logging.getLogger(__name__)

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', '/api/shared-services')
    click.echo(response.text + '\n')


@click.command(name="new", help="Create a new shared_service")
@click.option('--definition', help='JSON definition for the shared_service', required=False)
@click.option('--definition-file', help='File containing JSON definition for the shared_service', required=False, type=click.File("r"))
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
def shared_services_create(ctx, definition, definition_file, wait_for_completion):
    log = logging.getLogger(__name__)

    if definition is None:
        if definition_file is None:
            raise click.UsageError('Please specify either a definition or a definition file')
        definition = definition_file.read()

    definition_dict = json.loads(definition)

    client = ApiClient.get_api_client_from_config()
    click.echo("Creating shared_service...", err=True)
    response = client.call_api(log, 'POST', '/api/shared-services', json_data=definition_dict)

    if wait_for_completion:
        ctx.obj = SharedServiceOperationContext.from_operation_response(response)
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(shared_service_operation_show, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


@click.group(invoke_without_command=True, help="Perform actions on an individual shared_service")
@click.argument('shared_service_id', envvar='TRECLI_WORKSPACE_ID', required=True)
@click.pass_context
def shared_service(ctx: click.Context, shared_service_id: str, verify: bool) -> None:
    ctx.obj = {'shared_service_id': shared_service_id, 'verify': verify}


@click.command(name="show", help="Show a shared_service")
@click.pass_context
def shared_service_show(ctx: click.Context):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    shared_service_id = obj['shared_service_id']
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', f'/api/shared-services/{shared_service_id}', verify)
    click.echo(response.text + '\n')


@click.command(name="set-enabled", help="Delete a shared_service")
@click.option('--etag',
              help='The etag of the shared_service to update',
              required=True)
@click.option('--enable/--disable', is_flag=True, required=True)
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
def shared_service_set_enabled(ctx, etag, enable, wait_for_completion):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    shared_service_id = obj['shared_service_id']
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()
    click.echo(f"Setting isEnabled to {enable}...\n", err=True)
    response = client.call_api(
        log,
        'PATCH',
        f'/api/shared-services/{shared_service_id}',
        verify,
        headers={'etag': etag},
        json_data={'isEnabled': enable})
    if wait_for_completion:
        response_json = response.json()
        ctx.obj['shared_service_id'] = response_json['operation']['resourceId']
        ctx.obj['operation_id'] = response_json['operation']['id']
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(shared_service_operation_show, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


@click.command(name="delete", help="Delete a shared_service")
@click.option('--yes', is_flag=True, default=False)
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
def shared_service_delete(ctx, yes, wait_for_completion):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    shared_service_id = obj['shared_service_id']
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')
    verify = obj['verify']

    if not yes:
        click.confirm("Are you sure you want to delete this shared_service?", err=True, abort=True)

    client = ApiClient.get_api_client_from_config()
    click.echo("Deleting shared_service...\n", err=True)
    response = client.call_api(log, 'DELETE', f'/api/shared-services/{shared_service_id}', verify)
    if wait_for_completion:
        response_json = response.json()
        ctx.obj['operation_id'] = response_json['operation']['id']
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(shared_service_operation_show, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


shared_services.add_command(shared_services_list)
shared_services.add_command(shared_services_create)
