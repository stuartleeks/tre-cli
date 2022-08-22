import logging
import click
from tre.commands.operation import get_operation_id_completion, operation_show
from tre.output import output_option, query_option
from tre.api_client import ApiClient

from .contexts import pass_user_resource_operation_context, UserResourceOperationContext


def operation_id_completion(ctx, param, incomplete):
    log = logging.getLogger(__name__)
    parent_ctx = ctx.parent
    workspace_service_id = parent_ctx.params["workspace_service_id"]
    parent2_ctx = parent_ctx.parent
    workspace_id = parent2_ctx.params["workspace_id"]
    list_url = f'/api/workspaces/{workspace_id}/workspace-services/{workspace_service_id}/operations'

    client = ApiClient.get_api_client_from_config()
    workspace_scope = client.get_workspace_scope(log, workspace_id)

    return get_operation_id_completion(ctx, log, list_url, param, incomplete, scope_id=workspace_scope)


@click.group(name="operation", invoke_without_command=True, help="Perform actions on an operation")
@click.argument('operation_id', required=True, type=click.UUID, shell_complete=operation_id_completion)
@click.pass_context
def user_resource_operation(ctx: click.Context, operation_id) -> None:
    ctx.obj = UserResourceOperationContext.add_operation_id_to_context_obj(ctx, operation_id)


@click.command(name="show", help="Show user resource operation")
@click.option('--wait-for-completion',
              help="If an operation is in progress, wait for it to complete (when operation_id is specified)",
              flag_value=True,
              default=False)
@output_option()
@query_option()
@pass_user_resource_operation_context
def user_resource_operation_show(user_resource_operation_context: UserResourceOperationContext, wait_for_completion, output_format, query, suppress_output: bool = False) -> None:
    log = logging.getLogger(__name__)

    workspace_id = user_resource_operation_context.workspace_id
    if workspace_id is None:
        raise click.UsageError('Missing workspace ID')
    workspace_service_id = user_resource_operation_context.workspace_service_id
    if workspace_service_id is None:
        raise click.UsageError('Missing workspace-service ID')
    user_resource_id = user_resource_operation_context.user_resource_id
    if user_resource_id is None:
        raise click.UsageError('Missing user-resource ID')
    operation_id = user_resource_operation_context.operation_id
    if operation_id is None:
        raise click.UsageError('Missing operation ID')

    client = ApiClient.get_api_client_from_config()
    workspace_scope = client.get_workspace_scope(log, workspace_id)

    operation_url = f'/api/workspaces/{workspace_id}/workspace-services/{workspace_service_id}/user-resources/{user_resource_id}/operations/{operation_id}'
    operation_show(log, operation_url, wait_for_completion, output_format, query, suppress_output, scope_id=workspace_scope)


user_resource_operation.add_command(user_resource_operation_show)
