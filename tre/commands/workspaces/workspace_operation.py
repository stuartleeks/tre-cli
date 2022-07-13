import logging
import click
from tre.api_client import ApiClient
from time import sleep

from tre.output import output

from .workspace_contexts import pass_workspace_operation_context, WorkspaceOperationContext


def is_operational_state_terminal(state: str) -> bool:
    # Test against 'active' states
    # This way, a new state will be considered terminal (and not a success)
    # so we avoid a case where --wait-for-completion continues indefinitely
    # when there is a new state (and we return a non-successful status to
    # highlight it)
    return state not in [
        'deleting',
        'deploying',
        'invoking_action',
        'pipeline_deploying',
        'not_deployed',
        'awaiting_deletion'
    ]


def is_operational_state_success(state: str) -> bool:
    return state in [
        'deleted',
        'deployed',
        'action_succeeded',
        'pipeline_succeeded',
    ]


@click.group(name="operation", invoke_without_command=True, help="Perform actions on an operation")
@click.argument('operation_id', required=True)
@click.pass_context
def workspace_operation(ctx: click.Context, operation_id) -> None:
    ctx.obj = WorkspaceOperationContext.add_operation_id_to_context_obj(ctx, operation_id)


@click.command(name="show", help="Workspace operation")
@click.option('--wait-for-completion',
              help="If an operation is in progress, wait for it to complete (when operation_id is specified)",
              flag_value=True,
              default=False)
@click.option('--output', '-o', 'output_format', default='json', type=click.Choice(['json', 'none']), help="Output format")
@click.option('--query', '-q', default=None, help="JMESPath query to apply to the result")
@pass_workspace_operation_context
def workspace_operation_show(workspace_operation_context: WorkspaceOperationContext, wait_for_completion, output_format, query, suppress_output: bool = False) -> None:
    log = logging.getLogger(__name__)

    workspace_id = workspace_operation_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    operation_id = workspace_operation_context.operation_id
    if operation_id is None:
        raise click.UsageError('Missing operation ID')

    client = ApiClient.get_api_client_from_config()

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/operations/{operation_id}',
    )
    response_json = response.json()
    action = response_json['operation']['action']
    state = response_json['operation']['status']

    while wait_for_completion and not is_operational_state_terminal(state):
        click.echo(f'Operation state: {state} (action={action})',
                   err=True, nl=False)
        sleep(5)
        click.echo(' - refreshing...', err=True)
        response = client.call_api(
            log,
            'GET',
            f'/api/workspaces/{workspace_id}/operations/{operation_id}',
        )
        response_json = response.json()
        action = response_json['operation']['action']
        state = response_json['operation']['status']

    if not suppress_output:
        output(response.text, output_format=output_format, query=query)


workspace_operation.add_command(workspace_operation_show)
