import json
import click
import logging

from tre.api_client import ApiClient
from tre.commands.workspaces.contexts import pass_workspace_context
from tre.output import output


@click.group(help="List/add airlocks")
def airlocks() -> None:
    pass


@click.command(name="list", help="List airlocks")
@click.option('--output', '-o', 'output_format', default='json', type=click.Choice(['table', 'json', 'none']), help="Output format")
@click.option('--query', '-q', default=None, help="JMESPath query to apply to the result")
@pass_workspace_context
def airlocks_list(workspace_context, output_format, query):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    client = ApiClient.get_api_client_from_config()
    workspace_scope = client.get_workspace_scope(log, workspace_id)

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/requests',
        scope_id=workspace_scope,
    )
    output(response.text, output_format=output_format, query=query)


@click.command(name="new", help="Create a new airlock request")
@click.option('--definition', help='JSON definition for the request', required=False)
@click.option('--definition-file', help='File containing JSON definition for the request', required=False, type=click.File("r"))
@click.option('--output', '-o', 'output_format', default='json', type=click.Choice(['table', 'json', 'none']), help="Output format")
@click.option('--query', '-q', default=None, help="JMESPath query to apply to the result")
@pass_workspace_context
def airlock_create(workspace_context, definition, definition_file, output_format, query):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    if definition is None:
        if definition_file is None:
            raise click.UsageError('Please specify either a definition or a definition file')
        definition = definition_file.read()

    definition_dict = json.loads(definition)

    client = ApiClient.get_api_client_from_config()
    workspace_scope = client.get_workspace_scope(log, workspace_id)

    click.echo("Creating airlock request...", err=True)
    response = client.call_api(
        log,
        'POST',
        f'/api/workspaces/{workspace_id}/requests',
        json_data=definition_dict,
        scope_id=workspace_scope)

    output(response.text, output_format=output_format, query=query)
    return response.text


airlocks.add_command(airlocks_list)
airlocks.add_command(airlock_create)
