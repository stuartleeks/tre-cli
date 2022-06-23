import logging
import click
from tre.api_client import ApiClient
from time import sleep


def IsOperationStateTerminal(state: str) -> bool:
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
    ]


def IsOperationStateSuccess(state: str) -> bool:
    return state in [
        'deleted',
        'deployed',
        'action_succeeded',
        'pipeline_succeeded',
    ]


@click.command(name="operations", help="Workspace operations")
@click.argument('operation_id', required=False)
@click.option('--wait-for-completion',
              help="If an operation is in progress, wait for it to complete (when operation_id is specified)",
              flag_value=True,
              default=False)
@click.pass_context
def workspace_operations(ctx, operation_id, wait_for_completion):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    workspace_id = obj['workspace_id']
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()
    if operation_id is None:
        # list
        response = client.call_api(
            log,
            'GET',
            f'/api/workspaces/{workspace_id}/operations',
            verify
        )
        click.echo(response.text + '\n')
    else:
        # show
        response = client.call_api(
            log,
            'GET',
            f'/api/workspaces/{workspace_id}/operations/{operation_id}',
            verify)
        response_json = response.json()
        action = response_json['operation']['action']
        state = response_json['operation']['status']

        while wait_for_completion and not IsOperationStateTerminal(state):
            click.echo(f'Operation state: {state} (action={action})',
                       err=True, nl=False)
            sleep(5)
            click.echo(' - refreshing...', err=True)
            response = client.call_api(
                log,
                'GET',
                f'/api/workspaces/{workspace_id}/operations/{operation_id}',
                verify)
            response_json = response.json()
            action = response_json['operation']['action']
            state = response_json['operation']['status']

        click.echo(response.text + '\n')
