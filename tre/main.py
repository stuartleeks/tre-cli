import click

from tre.commands.login import login
from tre.commands.api_call import call_api
from tre.commands.workspaces.workspace import workspace
from tre.commands.workspaces.workspaces import workspaces


@click.group()
def cli():
    pass


cli.add_command(login)
cli.add_command(call_api)
cli.add_command(workspaces)
cli.add_command(workspace)

if __name__ == "__main__":
    cli()
