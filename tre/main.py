import click

from tre.commands.login import login
from tre.commands.api_call import call_api
from tre.commands.workspace import workspaces


@click.group()
def cli():
    pass


cli.add_command(login)
cli.add_command(call_api)
cli.add_command(workspaces)

if __name__ == "__main__":
    cli()
