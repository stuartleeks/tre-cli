import logging
import click
from tre.api_client import ApiClient
from tre.output import output, output_option, query_option

from .contexts import UserResourceContext, pass_user_resource_context
from .operation import user_resource_operation
from .operations import user_resource_operations


def user_resource_id_completion(ctx: click.Context, param, incomplete):
    log = logging.getLogger(__name__)
    parent_ctx = ctx.parent
    workspace_service_id = parent_ctx.params["workspace_service_id"]
    parent2_ctx = parent_ctx.parent
    workspace_id = parent2_ctx.params["workspace_id"]

    client = ApiClient.get_api_client_from_config()
    workspace_scope = client.get_workspace_scope(log, workspace_id)
    response = client.call_api(log, 'GET', f'/api/workspaces/{workspace_id}/workspace-services/{workspace_service_id}/user-resources', scope_id=workspace_scope)
    if response.is_success:
        ids = [resource["id"] for resource in response.json()["userResources"]]
        return [id for id in ids if id.startswith(incomplete)]


@click.group(name="user-resource", invoke_without_command=True, help="Perform actions on a user resource")
@click.argument('user_resource_id', required=True, type=click.UUID, shell_complete=user_resource_id_completion)
@click.pass_context
def user_resource(ctx: click.Context, user_resource_id) -> None:
    ctx.obj = UserResourceContext.add_user_resource_id_to_context_obj(ctx, user_resource_id)


@click.command(name="show", help="Show user resource")
@output_option()
@query_option()
@pass_user_resource_context
def user_resource_show(user_resource_context: UserResourceContext, output_format, query) -> None:
    log = logging.getLogger(__name__)

    workspace_id = user_resource_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    workspace_service_id = user_resource_context.workspace_service_id
    if workspace_service_id is None:
        raise click.UsageError('Missing workspace service ID')
    user_resource_id = user_resource_context.user_resource_id
    if user_resource_id is None:
        raise click.UsageError('Missing user resource ID')

    client = ApiClient.get_api_client_from_config()
    workspace_scope = client.get_workspace_scope(log, workspace_id)

    response = client.call_api(
        log,
        'GET',
        f'/api/workspaces/{workspace_id}/workspace-services/{workspace_service_id}/user-resources/{user_resource_id}',
        scope_id=workspace_scope,
    )

    # TODO table query
    output(response.text, output_format=output_format, query=query, default_table_query=r"userResource")


user_resource.add_command(user_resource_show)
user_resource.add_command(user_resource_operation)
user_resource.add_command(user_resource_operations)


# TODO PATCH

# TODO - DELETE

# TODO - invoke action
