import click

from tre.commands.get_token import get_token
from tre.commands.login import login
from tre.commands.api_call import call_api
from tre.commands.workspaces.workspace import workspace
from tre.commands.workspaces.workspaces import workspaces
from tre.commands.shared_services.shared_service import shared_service
from tre.commands.shared_services.shared_services import shared_services

from tre.commands.workspace_templates.workspace_templates import workspace_templates
from tre.commands.workspace_templates.workspace_template import workspace_template
from tre.commands.shared_service_templates.shared_service_templates import shared_service_templates
from tre.commands.shared_service_templates.shared_service_template import shared_service_template
from tre.commands.workspace_service_templates.workspace_service_templates import workspace_service_templates
from tre.commands.workspace_service_templates.workspace_service_template import workspace_service_template


@click.group()
def cli():
    pass


cli.add_command(login)
cli.add_command(call_api)
cli.add_command(workspaces)
cli.add_command(workspace)
cli.add_command(shared_services)
cli.add_command(shared_service)

cli.add_command(workspace_templates)
cli.add_command(workspace_template)
cli.add_command(shared_service_templates)
cli.add_command(shared_service_template)
cli.add_command(workspace_service_templates)
cli.add_command(workspace_service_template)

cli.add_command(get_token)

# TODO - costs endpoints
# TODO - workspace service endpoints
# TODO - workspaces service templates
# TODO - user resource templates
# TODO - health
# TODO - migrations?

if __name__ == "__main__":
    cli()
