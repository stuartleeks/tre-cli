import logging
import click
from tre.api_client import ApiClient
from tre.output import output

from .contexts import WorkspaceContext, pass_workspace_context


@click.group(name="operations", help="List operations ")
def workspace_operations():
    pass


@click.command(name="list", help="List workspace operations")
@click.option('--output', '-o', 'output_format', default='json', type=click.Choice(['json', 'none']), help="Output format")
@click.option('--query', '-q', default=None, help="JMESPath query to apply to the result")
@pass_workspace_context
def workspace_operations_list(workspace_context: WorkspaceContext, output_format, query):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    client = ApiClient.get_api_client_from_config()

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/operations',
    )
    output(response.text, output_format=output_format, query=query)


workspace_operations.add_command(workspace_operations_list)
