import logging
import json
from pathlib import Path

import click

from tre.api_client import ApiClient


@click.command(name="login", help="Set the TRE credentials and base URL")
@click.option('--base-url',
              required=True,
              help='The TRE base URL, e.g. ' +
              'https://<id>.<location>.cloudapp.azure.com/')
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
def login(base_url, client_id, client_secret, aad_tenant_id, api_scope):
    """login"""
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
        'client-id': client_id,
        'client-secret': client_secret,
        'aad-tenant-id': aad_tenant_id,
        'api-scope': api_scope
    }

    # ensure ~/.config/tre folder exists
    Path('~/.config/tre').expanduser().mkdir(parents=True, exist_ok=True)
    Path('~/.config/tre/environment.json').expanduser().write_text(
        json.dumps(environment_config, indent=4),
        encoding='utf-8')

    click.echo('Login details saved\n')
