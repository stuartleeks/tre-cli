import logging
import click
from tre.api_client import ApiClient
from time import sleep

from .shared_service_contexts import pass_shared_service_operation_context, SharedServiceOperationContext


def is_operation_state_terminal(state: str) -> bool:
    # Test against 'active' states
    # This way, a new state will be considered terminal (and not a success)
    # so we avoid a case where --wait-for-completion continues indefinitely
    # when there is a new state (and we return a non-successful status to
    # highlight it)
    return state not in [
        'deleting',
        'deploying',
        'awaiting_action',
        'invoking_action',
        'pipeline_deploying',
        'not_deployed',
    ]


def is_operation_state_success(state: str) -> bool:
    return state in [
        'deleted',
        'deployed',
        'action_succeeded',
        'pipeline_succeeded',
    ]


@click.group(name="operation", invoke_without_command=True, help="Perform actions on an operation")
@click.argument('operation_id', required=True)
@click.pass_context
def shared_service_operation(ctx: click.Context, operation_id) -> None:
    ctx.obj = SharedServiceOperationContext.add_operation_id_to_context_obj(ctx, operation_id)


@click.command(name="show", help="SharedService operation")
@click.option('--wait-for-completion',
              help="If an operation is in progress, wait for it to complete (when operation_id is specified)",
              flag_value=True,
              default=False)
@pass_shared_service_operation_context
def shared_service_operation_show(shared_service_operation_context: SharedServiceOperationContext, wait_for_completion, suppress_output: bool = False):
    log = logging.getLogger(__name__)

    shared_service_id = shared_service_operation_context.shared_service_id
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')
    operation_id = shared_service_operation_context.operation_id
    if operation_id is None:
        raise click.UsageError('Missing operation ID')

    client = ApiClient.get_api_client_from_config()

    response = client.call_api(
        log,
        'GET',
        f'/api/shared-services/{shared_service_id}/operations/{operation_id}',
    )
    response_json = response.json()
    action = response_json['operation']['action']
    state = response_json['operation']['status']

    while wait_for_completion and not is_operation_state_terminal(state):
        click.echo(f'Operation state: {state} (action={action})',
                   err=True, nl=False)
        sleep(5)
        click.echo(' - refreshing...', err=True)
        response = client.call_api(
            log,
            'GET',
            f'/api/shared-services/{shared_service_id}/operations/{operation_id}',
        )
        response_json = response.json()
        action = response_json['operation']['action']
        state = response_json['operation']['status']

    if not suppress_output:
        click.echo(response.text + '\n')


shared_service_operation.add_command(shared_service_operation_show)
