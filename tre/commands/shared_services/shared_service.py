import click
import logging

from tre.api_client import ApiClient
from .shared_service_contexts import pass_shared_service_context, SharedServiceContext

from .shared_service_operation import SharedServiceOperationContext, shared_service_operation_show, shared_service_operation
from .shared_service_operations import shared_service_operations


@click.group(invoke_without_command=True, help="Perform actions on an individual shared_service")
@click.argument('shared_service_id', envvar='TRECLI_WORKSPACE_ID', required=True)
@click.pass_context
def shared_service(ctx: click.Context, shared_service_id: str) -> None:
    ctx.obj = SharedServiceContext(shared_service_id)


@click.command(name="show", help="Show a shared_service")
@pass_shared_service_context
def shared_service_show(shared_service_context: SharedServiceContext):
    log = logging.getLogger(__name__)

    shared_service_id = shared_service_context.shared_service_id
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(log, 'GET', f'/api/shared-services/{shared_service_id}', )
    click.echo(response.text + '\n')


@click.command(name="invoke-action", help="Invoke an action on a shared_service")
@click.argument('action-name', required=True)
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@click.pass_context
@pass_shared_service_context
def shared_service_invoke_action(shared_service_context: SharedServiceContext, ctx: click.Context, action_name, wait_for_completion):
    log = logging.getLogger(__name__)

    shared_service_id = shared_service_context.shared_service_id
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')

    client = ApiClient.get_api_client_from_config()
    click.echo(f"Invoking action {action_name}...\n", err=True)
    response = client.call_api(
        log,
        'POST',
        f'/api/shared-services/{shared_service_id}/invoke-action?action={action_name}'
    )
    if wait_for_completion:
        ctx.obj = SharedServiceOperationContext.from_operation_response(response)
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
@pass_shared_service_context
def shared_service_delete(shared_service_context: SharedServiceContext, ctx: click.Context, yes, wait_for_completion):
    log = logging.getLogger(__name__)

    shared_service_id = shared_service_context.shared_service_id
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')

    if not yes:
        click.confirm("Are you sure you want to delete this shared_service?", err=True, abort=True)

    client = ApiClient.get_api_client_from_config()
    click.echo("Deleting shared_service...\n", err=True)
    response = client.call_api(log, 'DELETE', f'/api/shared-services/{shared_service_id}')
    if wait_for_completion:
        ctx.obj = SharedServiceOperationContext.from_operation_response(response)
        click.echo("Waiting for completion...", err=True)
        ctx.invoke(shared_service_operation_show, wait_for_completion=True)
    else:
        click.echo(response.text + '\n')


shared_service.add_command(shared_service_show)
shared_service.add_command(shared_service_invoke_action)
shared_service.add_command(shared_service_delete)
shared_service.add_command(shared_service_operations)
shared_service.add_command(shared_service_operation)