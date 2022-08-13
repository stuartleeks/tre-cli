import click
import json
import logging
import msal
import os

from pathlib import Path

from tre.api_client import ApiClient


@click.group(name="login", help="Set the TRE credentials and base URL")
def login():
    pass


@click.command(name="device-code", help="Use client credentials flow (client ID + secret) to authenticate")
@click.option('--base-url',
              required=True,
              help='The TRE base URL, e.g. '
              + 'https://<id>.<location>.cloudapp.azure.com/')
@click.option('--client-id',
              required=True,
              help='The Client ID of the Azure AD application for the API')
@click.option('--aad-tenant-id',
              required=True,
              help='The Tenant ID for the AAD tenant to authenticate with')
@click.option('--api-scope',
              required=True,
              help='The API scope for the base API')
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)
@click.option('--workspace', "workspaces",
              required=False,
              help='Additionally log in to workspace with specified id (can be specified multiple times).',
              multiple=True)
@click.option('--all-workspaces',
              required=False,
              default=False,
              is_flag=True,
              help='Additionally log in to all current workspaces (not compatible with --workspace)')
def login_device_code(base_url: str, client_id: str, aad_tenant_id: str, api_scope: str, verify: bool, workspaces: list[str], all_workspaces):
    log = logging.getLogger(__name__)

    if workspaces is not None and len(workspaces) > 0:
        if all_workspaces:
            raise click.ClickException("Cannot use `--all-workspaces and --workspace")

    # Set up token cache
    Path('~/.config/tre').expanduser().mkdir(parents=True, exist_ok=True)
    token_cache_file = Path('~/.config/tre/token_cache.json').expanduser()

    cache = msal.SerializableTokenCache()
    if os.path.exists(token_cache_file):
        cache.deserialize(open(token_cache_file, "r").read())

    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{aad_tenant_id}",
        token_cache=cache)

    click.echo(f'api_scope: {api_scope}')
    flow = app.initiate_device_flow(scopes=[api_scope])
    if "user_code" not in flow:
        raise click.ClickException("unable to initiate device flow")

    click.echo(flow['message'])
    app.acquire_token_by_device_flow(flow)

    # Save the auth details to ~/.config/tre/environment.json
    environment_config = {
        'base-url': base_url,
        'login-method': 'device-code',
        'token-cache-file': str(token_cache_file.absolute()),
        'client-id': client_id,
        'aad-tenant-id': aad_tenant_id,
        'api-scope': api_scope,
        'verify': verify,
    }
    Path('~/.config/tre/environment.json').expanduser().write_text(
        json.dumps(environment_config, indent=4),
        encoding='utf-8')

    # Save the token cache
    if cache.has_state_changed:
        with open(token_cache_file, "w") as cache_file:
            cache_file.write(cache.serialize())

    client = None

    if all_workspaces:
        click.echo("Getting current workspaces: ...")
        client = ApiClient.get_api_client_from_config()
        response = client.call_api(log, "GET", "/api/workspaces")
        if not response.is_success:
            raise click.ClickException(f"Failed to list workspaces: {response.text}")
        workspaces = [workspace["id"] for workspace in response.json()["workspaces"] if "scope_id" in workspace["properties"]]

    if workspaces is not None and len(workspaces) > 0:
        click.echo(f"Logging in to workspaces: {workspaces}...")
        if client is None:
            client = ApiClient.get_api_client_from_config()

        workspace_scopes = [client.get_workspace_scope(log, workspace) for workspace in workspaces]

        flow = app.initiate_device_flow(scopes=[api_scope] + workspace_scopes)
        if "user_code" not in flow:
            raise click.ClickException("unable to initiate device flow")

        click.echo(flow['message'])
        app.acquire_token_by_device_flow(flow)

        if cache.has_state_changed:
            with open(token_cache_file, "w") as cache_file:
                cache_file.write(cache.serialize())

    click.echo("Successfully logged in")


@click.command(name="client-credentials", help="Use client credentials flow (client ID + secret) to authenticate")
@click.option('--base-url',
              required=True,
              help='The TRE base URL, e.g. '
              + 'https://<id>.<location>.cloudapp.azure.com/')
@click.option('--client-id',
              required=True,
              help='The Client ID to use for authenticating')
@click.option('--client-secret',
              required=True,
              help='The Client Secret to use for authenticating')
@click.option('--aad-tenant-id',
              required=True,
              help='The Tenant ID for the AAD tenant to authenticate with')
@click.option('--api-scope',
              required=True,
              help='The API scope for the base API')
@click.option('--verify/--no-verify',
              help='Enable/disable SSL verification',
              default=True)
def login_client_credentials(base_url: str, client_id: str, client_secret: str, aad_tenant_id: str, api_scope: str, verify: bool):
    log = logging.getLogger(__name__)
    # Test the auth succeeds
    try:
        log.info("Attempting sign-in...")
        ApiClient.get_auth_token_client_credentials(log,
                                                    client_id,
                                                    client_secret,
                                                    aad_tenant_id,
                                                    api_scope)
        log.info("Sign-in successful")
        # TODO make a call against the API to ensure the auth token
        # is valid there (url)
    except RuntimeError:
        log.error("Sign-in failed")
        click.echo("Sign-in failed\n")
        return

    # Save the auth details to ~/.config/tre/environment.json
    environment_config = {
        'base-url': base_url,
        'login-method': 'client-credentials',
        'client-id': client_id,
        'client-secret': client_secret,
        'aad-tenant-id': aad_tenant_id,
        'api-scope': api_scope,
        'verify': verify,
    }

    # ensure ~/.config/tre folder exists
    Path('~/.config/tre').expanduser().mkdir(parents=True, exist_ok=True)
    Path('~/.config/tre/environment.json').expanduser().write_text(
        json.dumps(environment_config, indent=4),
        encoding='utf-8')

    click.echo('Login details saved\n')


login.add_command(login_client_credentials)
login.add_command(login_device_code)
