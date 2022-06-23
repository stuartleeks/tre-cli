import logging
import click
from tre.api_client import ApiClient
from time import sleep


@click.group(name="operation", help="Workspace operations")
def workspace_operation():
    pass


@click.command(name="list", help="List operations")
@click.option('--workspace-id',
              envvar='TRECLI_WORKSPACE_ID',
              help='The ID of the workspace to show operations for',
              required=True)
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)
def workspace_operation_list(workspace_id, verify):
    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()
    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/operations',
        verify
    )
    click.echo(response.text + '\n')


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


@click.command(name="show", help="Show an operation")
@click.option('--workspace-id',
              help='The ID of the workspace to show operation for',
              envvar='TRECLI_WORKSPACE_ID',
              required=True)
@click.option('--operation-id',
              help='The ID of the operation to show',
              envvar='TRECLI_OPERATION_ID',
              required=True)
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              envvar='TRECLI_VERIFY',
              default=True)
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
def workspace_operation_show(
        workspace_id,
        operation_id,
        verify,
        wait_for_completion):

    log = logging.getLogger(__name__)
    client = ApiClient.get_api_client_from_config()

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


workspace_operation.add_command(workspace_operation_list)
workspace_operation.add_command(workspace_operation_show)
