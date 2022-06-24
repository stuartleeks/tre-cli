import logging
import click
from tre.api_client import ApiClient

from .shared_service_contexts import SharedServiceContext, pass_shared_service_context


@click.group(name="operations", help="List operations ")
def shared_service_operations():
    pass


@click.command(name="list", help="List shared_service operations")
@pass_shared_service_context
def shared_service_operations_list(shared_service_context: SharedServiceContext):
    log = logging.getLogger(__name__)

    shared_service_id = shared_service_context.shared_service_id
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')

    client = ApiClient.get_api_client_from_config()

    response = client.call_api(
        log,
        'GET',
        f'/api/shared-services/{shared_service_id}/operations',
    )
    click.echo(response.text + '\n')


shared_service_operations.add_command(shared_service_operations_list)
