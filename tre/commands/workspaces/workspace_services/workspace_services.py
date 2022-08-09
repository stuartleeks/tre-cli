import logging
import click

from tre.api_client import ApiClient
from tre.output import output
from tre.commands.workspaces.contexts import pass_workspace_context


@click.group(name="workspace-services", help="List workspace-services ")
def workspace_workspace_services():
    pass


# TODO - table output
@click.command(name="list", help="List workspace services")
@click.option('--output', '-o', 'output_format', default='json', type=click.Choice(['json', 'none']), help="Output format")
@click.option('--query', '-q', default=None, help="JMESPath query to apply to the result")
@pass_workspace_context
def workspace_workspace_services_list(workspace_context, output_format, query):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    client = ApiClient.get_api_client_from_config()

    workspace_response = client.call_api(
        log,
        "GET",
        f'/api/workspaces/{workspace_id}',
    )
    workspace_json = workspace_response.json()
    workspace_scope = workspace_json["workspace"]["properties"]["scope_id"]

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/workspace-services',
        scope_id=workspace_scope,
    )
    output(response.text, output_format=output_format, query=query)


workspace_workspace_services.add_command(workspace_workspace_services_list)
