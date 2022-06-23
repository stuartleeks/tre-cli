import json
import click
from logging import Logger
from httpx import Client, Response
from pathlib import Path


class ApiClient:
    def __init__(self,
                 base_url: str,
                 client_id: str,
                 client_secret: str,
                 aad_tenant_id: str,
                 api_scope: str,
                 verify: bool):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.aad_tenant_id = aad_tenant_id
        self.api_scope = api_scope
        self.verify = verify

    @staticmethod
    def get_auth_token_client_credentials(log: Logger,
                                          client_id: str,
                                          client_secret: str,
                                          aad_tenant_id: str,
                                          api_scope: str):
        allow_insecure = True  # TODO add option?
        with Client(verify=not allow_insecure) as client:
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
    def get_api_client_from_config() -> Response:
        config_text = Path(
            '~/.config/tre/environment.json').expanduser().read_text(
                encoding='utf-8')
        config = json.loads(config_text)
        return ApiClient(
            config['base-url'],
            config['client-id'],
            config['client-secret'],
            config['aad-tenant-id'],
            config['api-scope'],
            config['verify'],
        )

    def get_auth_token(self, log: Logger, scope: str = None) -> str:
        return ApiClient.get_auth_token_client_credentials(
            log,
            self.client_id,
            self.client_secret,
            self.aad_tenant_id,
            scope or self.api_scope)

    def call_api(
        self,
        log: Logger,
        method: str,
        url: str,
        headers: dict[str, str] = {},
        json=None,
        scope_id: str = None,
        throw_on_error: bool = True,
    ) -> str:
        with Client(verify=self.verify) as client:
            headers = headers.copy()
            headers['Authorization'] = f"Bearer {self.get_auth_token(log, scope_id)}"
            response = client.request(method, f'{self.base_url}/{url}', headers=headers, json=json)
            if throw_on_error and response.is_error:
                raise click.ClickException(message=response.text)
            return response
