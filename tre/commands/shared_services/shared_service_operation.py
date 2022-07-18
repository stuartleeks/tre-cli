import logging
import click

from tre.commands.operation import operation_show

from .shared_service_contexts import pass_shared_service_operation_context, SharedServiceOperationContext


def is_operation_state_terminal(state: str) -> bool:
    # In the absence of a field on the operation indicating whether it is completed or not,
    # we maintain a list here.
    # Note that we test against 'active' states
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
@click.option('--output', '-o', 'output_format',
              help="Output format",
              type=click.Choice(['json', 'none']),
              default='json')
@click.option('--query', '-q',
              help="JMESPath query to apply to the result",
              default=None)
@pass_shared_service_operation_context
def shared_service_operation_show(shared_service_operation_context: SharedServiceOperationContext, wait_for_completion, output_format, query, suppress_output: bool = False):
    log = logging.getLogger(__name__)

    shared_service_id = shared_service_operation_context.shared_service_id
    if shared_service_id is None:
        raise click.UsageError('Missing shared_service ID')
    operation_id = shared_service_operation_context.operation_id
    if operation_id is None:
        raise click.UsageError('Missing operation ID')

    operation_url = f'/api/shared-services/{shared_service_id}/operations/{operation_id}'

    operation_show(log, operation_url, wait_for_completion, suppress_output, output_format=output_format, query=query)


shared_service_operation.add_command(shared_service_operation_show)
