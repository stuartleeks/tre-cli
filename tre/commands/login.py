import logging
import json
from pathlib import Path

from cliff.command import Command

from tre.api_client import ApiClient

class Login(Command):
    "Log in to a TRE environment"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        # https://docs.python.org/3/howto/argparse.html
        # https://docs.python.org/3/library/argparse.html
        parser = super(Login, self).get_parser(prog_name)

        # Base args
        parser.add_argument(
            '--base-url', nargs='?',
            help='The TRE base URL, e.g. https://<id>.<location>.cloudapp.azure.com/',
            required=True)

        # Currently, only allow a client-id/secret login flow
        # in future, consider a device-code flow (would require UI changes)
        parser.add_argument('--client-id',
                            nargs='?',
                            help='The Client ID to use for authenticating',
                            required=True)
        parser.add_argument('--client-secret',
                            nargs='?',
                            help='The Client Secret to use for authenticating',
                            required=True)
        parser.add_argument('--aad-tenant-id',
                            nargs='?',
                            help='The Tenant ID for the AAD tenant to authenticate with',
                            required=True)
        parser.add_argument('--api-scope',
                            nargs='?',
                            help='The API Scope',
                            required=True)

        return parser

    def take_action(self, parsed_args):
        # Test the auth succeeds
        try:
            self.log.info("Attempting sign-in...")
            ApiClient.get_auth_token_client_credentials(self.log,
                                     parsed_args.client_id,
                                     parsed_args.client_secret,
                                     parsed_args.aad_tenant_id,
                                     parsed_args.api_scope)
            self.log.info("Sign-in successful")
            # TODO make a call against the API to ensure the auth token is valid there (url)
        except RuntimeError:
            self.log.error("Sign-in failed")
            self.app.stdout.write("Sign-in failed\n")
            return

        # Save the auth details to ~/.config/tre/environment.json
        environment_config = {
            'base-url': parsed_args.base_url,
            'client-id': parsed_args.client_id,
            'client-secret': parsed_args.client_secret,
            'aad-tenant-id': parsed_args.aad_tenant_id,
            'api-scope': parsed_args.api_scope
        }

        # ensure ~/.config/tre folder exists
        Path('~/.config/tre').expanduser().mkdir(parents=True, exist_ok=True)
        Path('~/.config/tre/environment.json').expanduser().write_text(
            json.dumps(environment_config, indent=4),
            encoding='utf-8')

        self.app.stdout.write('Login details saved\n')


