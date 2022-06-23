import logging
import click
from tre.api_client import ApiClient


@click.command(name="workspace-services", help="Workspace services")
@click.argument('service_id', required=False)
@click.pass_context
def workspace_workspace_service(ctx, service_id):
    log = logging.getLogger(__name__)

    obj = ctx.obj
    workspace_id = obj['workspace_id']
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    verify = obj['verify']

    client = ApiClient.get_api_client_from_config()
    if service_id is None:
        # list
        response = client.call_api(
            log,
            'GET',
            f'/api/workspaces/{workspace_id}/workspace-services',
            verify
        )
        click.echo(response.text + '\n')
    else:
        # show
        response = client.call_api(
            log,
            'GET',
            f'/api/workspaces/{workspace_id}/workspace-services/{service_id}',
            verify)
        click.echo(response.text + '\n')
