import json
import logging
import click

from tre.api_client import ApiClient
from tre.commands.operation import operation_show
from tre.commands.workspaces.contexts import WorkspaceContext, pass_workspace_context
from tre.output import output, output_option, query_option


@click.group(name="workspace-services", help="List workspace-services ")
def workspace_workspace_services():
    pass


# TODO - table output
@click.command(name="list", help="List workspace services")
@output_option()
@query_option()
@pass_workspace_context
def workspace_workspace_services_list(workspace_context, output_format, query):
    log = logging.getLogger(__name__)

    workspace_id = workspace_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')

    client = ApiClient.get_api_client_from_config()

    workspace_scope = client.get_workspace_scope(log, workspace_id)

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/workspace-services',
        scope_id=workspace_scope,
    )
    output(response.text, output_format=output_format, query=query, default_table_query=r"workspaceServices[].{id:id,template_name:templateName,template_version:templateVersion,sdeployment_status:deploymentStatus}")


@click.command(name="new", help="Create a new workspace-service")
@click.option('--definition', help='JSON definition for the workspace', required=False)
@click.option('--definition-file', help='File containing JSON definition for the workspace', required=False, type=click.File("r"))
@click.option('--wait-for-completion',
              flag_value=True,
              default=False)
@output_option()
@query_option()
@pass_workspace_context
def workspace_workspace_services_create(workspace_context: WorkspaceContext, definition, definition_file, wait_for_completion, output_format, query):
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
    click.echo("Creating workspace-service...", err=True)
    response = client.call_api(
        log,
        'POST',
        f'/api/workspaces/{workspace_id}/workspace-services',
        json_data=definition_dict,
        scope_id=workspace_scope
    )

    if wait_for_completion:
        operation_url = response.headers['location']
        operation_show(log, operation_url, wait_for_completion=True, output_format=output_format, query=query)
    else:
        output(response.text, output_format=output_format, query=query)
        return response.text


workspace_workspace_services.add_command(workspace_workspace_services_list)
workspace_workspace_services.add_command(workspace_workspace_services_create)
