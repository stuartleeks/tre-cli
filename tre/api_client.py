import click
import json
import msal
import os

from typing import Callable
from httpx import Client, Response
from logging import Logger
from pathlib import Path


class ApiException(click.ClickException):
    """An exception that Click can handle and show to the user containing API call error info."""

    # Use exit code 2 for API errors that are JSON
    exit_code = 2

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def show(self, file=None) -> None:
        # Write (JSON) message stdout without any extra info to allow callers to parse it
        click.echo(self.message, file=file)


class ApiClient:
    def __init__(self,
                 base_url: str,
                 get_auth_token: "Callable[[Logger, str], str]",
                 verify: bool):
        self.base_url = base_url
        self.verify = verify
        self.get_auth_token = get_auth_token

    @staticmethod
    def get_auth_token_client_credentials(log: Logger,
                                          client_id: str,
                                          client_secret: str,
                                          aad_tenant_id: str,
                                          api_scope: str):
        with Client() as client:
            headers = {'Content-Type': "application/x-www-form-urlencoded"}
            # Use Client Credentials flow
            payload = f"grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}&scope={api_scope}/.default"
            url = f"https://login.microsoftonline.com/{aad_tenant_id}/oauth2/v2.0/token"

            log.debug('POSTing to token endpoint')
            response = client.post(url, headers=headers, content=payload)
            try:
                if response.status_code == 200:
                    log.debug('Parsing response')
                    response_json = response.json()
                    token = response_json["access_token"]
                    return token
                msg = f"Sign-in failed: {response.status_code}: {response.text}"
                log.error(msg)
                raise RuntimeError(msg)
            except json.JSONDecodeError:
                log.debug(
                    f'Failed to parse response as JSON: {response.content}')

        raise RuntimeError("Failed to get auth token")

    @staticmethod
    def get_auth_token_msal(log: Logger,
                            token_cache_file: str,
                            client_id: str,
                            aad_tenant_id: str,
                            scope: str):

        cache = msal.SerializableTokenCache()
        if os.path.exists(token_cache_file):
            cache.deserialize(open(token_cache_file, "r").read())

        app = msal.PublicClientApplication(
            client_id=client_id,
            authority=f"https://login.microsoftonline.com/{aad_tenant_id}",
            token_cache=cache)

        accounts = app.get_accounts()
        if accounts:
            auth_result = app.acquire_token_silent(scopes=[scope], account=accounts[0])
            if cache.has_state_changed:
                open(token_cache_file, "w").write(cache.serialize())
            return auth_result["access_token"]

        raise RuntimeError("Failed to get auth token")

    @staticmethod
    def get_api_client_from_config() -> Response:

        config_path = Path("~/.config/tre/environment.json").expanduser()
        if not config_path.exists():
            raise click.ClickException(
                "You need to log in (tre login) before calling this command"
            )

        config_text = config_path.read_text(encoding="utf-8")
        config = json.loads(config_text)

        login_method = config["login-method"]
        if login_method == "client-credentials":
            def get_auth_token(log, scope):
                return ApiClient.get_auth_token_client_credentials(
                    log,
                    config["client-id"],
                    config["client-secret"],
                    config["aad-tenant-id"],
                    scope or config["api-scope"]
                )
        elif login_method == "device-code":
            def get_auth_token(log, scope):
                return ApiClient.get_auth_token_msal(
                    log,
                    config["token-cache-file"],
                    config["client-id"],
                    config["aad-tenant-id"],
                    scope or config["api-scope"]
                )
        else:
            raise click.ClickException(f"Unhandled login method: {login_method}")

        return ApiClient(
            config["base-url"],
            get_auth_token,
            config["verify"],
        )

    def call_api(
        self,
        log: Logger,
        method: str,
        url: str,
        headers: "dict[str, str]" = {},
        json_data=None,
        scope_id: str = None,
        throw_on_error: bool = True,
    ) -> Response:
        with Client(verify=self.verify) as client:
            headers = headers.copy()
            headers['Authorization'] = f"Bearer {self.get_auth_token(log, scope_id)}"
            response = client.request(method, f'{self.base_url}/{url}', headers=headers, json=json_data)
            if throw_on_error and response.is_error:
                error_info = {
                    'status_code': response.status_code,
                    'body': response.text,
                }
                raise ApiException(message=json.dumps(error_info, indent=2))
            return response
