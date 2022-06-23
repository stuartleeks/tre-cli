import click
from httpx import Response


class WorkspaceContext(object):
    def __init__(self, workspace_id: str):
        self.workspace_id = workspace_id


pass_workspace_context = click.make_pass_decorator(WorkspaceContext)


class WorkspaceOperationContext(object):
    def __init__(self, workspace_id: str, operation_id: str):
        self.workspace_id = workspace_id
        self.operation_id = operation_id

    @staticmethod
    def from_operation_response(response: Response) -> "WorkspaceOperationContext":
        response_json = response.json()
        return WorkspaceOperationContext(
            workspace_id=response_json["operation"]["resourceId"],
            operation_id=response_json["operation"]["id"],
        )

    @staticmethod
    def add_operation_id_to_context_obj(ctx: click.Context, operation_id: str) -> "WorkspaceOperationContext":
        workspace_context = ctx.find_object(WorkspaceContext)
        return WorkspaceOperationContext(workspace_context.workspace_id, operation_id)


pass_workspace_operation_context = click.make_pass_decorator(WorkspaceOperationContext)


class WorkspaceWorkspaceServiceContext(object):
    def __init__(self, workspace_id: str, service_id: str):
        self.workspace_id = workspace_id
        self.service_id = service_id

    @staticmethod
    def add_service_id_to_context_obj(ctx: click.Context, service_id: str) -> "WorkspaceWorkspaceServiceContext":
        workspace_context = ctx.find_object(WorkspaceContext)
        return WorkspaceWorkspaceServiceContext(workspace_context.workspace_id, service_id)


pass_workspace_workspace_service_context = click.make_pass_decorator(WorkspaceWorkspaceServiceContext)