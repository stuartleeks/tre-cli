import click
import jmespath
import json

from enum import Enum


class OutputFormat(Enum):
    # TODO - add pretty JSON? (format & colour)
    Suppress = 'none'
    Json = 'json'


def output(result_json, output_format: OutputFormat = OutputFormat.Json, query: str = None) -> None:
    if output_format == OutputFormat.Suppress.value:
        return

    if query is None:
        output_json = result_json
    else:
        result = json.loads(result_json)
        output = jmespath.search(query, result)
        output_json = json.dumps(output)

    click.echo(output_json)
