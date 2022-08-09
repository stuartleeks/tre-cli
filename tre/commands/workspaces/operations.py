import logging
import click
from tre.commands.operation import operations_list

from .contexts import WorkspaceContext, pass_workspace_context


@click.group(name="operations", help="List operations ")
def workspace_operations():
    pass


@click.command(name="list", help="List workspace operations")
@click.option('--output', '-o', 'output_format', default='json', type=click.Choice(['table', 'json', 'none']), help="Output format")
@click.option('--query', '-q', default=None, help="JMESPath query to apply to the result")
@pass_workspace_context
def workspace_operations_list(workspace_context: WorkspaceContext, output_format, query):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    operations_url = f'/api/workspaces/{workspace_id}/operations'
    operations_list(log, operations_url, output_format, query)


workspace_operations.add_command(workspace_operations_list)
