import logging
from cliff.command import Command
from tre.api_client import ApiClient

class ApiCall(Command):
    "Issue an API call to the TRE environment"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(ApiCall, self).get_parser(prog_name)
        # Base args
        parser.add_argument(
            '--url', nargs='?',
            help='The API url TRE URL, e.g. https://<id>.<location>.cloudapp.azure.com/',
            required=True)

        parser.add_argument('--scope',
                            nargs='?',
                            help='The API scope',
                            required=False)
        return parser

    def take_action(self, parsed_args):
        # self.app.stdout.write('hello!\n')
        client = ApiClient.get_api_client_from_config()
        response = client.call_api(self.log, parsed_args.url, parsed_args.scope)
        self.app.stdout.write(response.text + '\n')