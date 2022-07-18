from time import sleep

import click
from tre.api_client import ApiClient
from tre.output import output


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


def operation_show(log, operation_url, wait_for_completion, output_format, query, suppress_output: bool = False):

    client = ApiClient.get_api_client_from_config()
    response = client.call_api(
        log,
        'GET',
        operation_url
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
            operation_url
        )
        response_json = response.json()
        action = response_json['operation']['action']
        state = response_json['operation']['status']

    if not suppress_output:
        output(response.text, output_format=output_format, query=query)

    return response.text
