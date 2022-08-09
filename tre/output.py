import click
import jmespath
import json
from tabulate import tabulate

from enum import Enum


class OutputFormat(Enum):
    # TODO - add pretty JSON? (format & colour)
    Suppress = 'none'
    Json = 'json'
    Table = 'table'


def output(result_json, output_format: OutputFormat = OutputFormat.Json, query: str = None, default_table_query: str = None) -> None:
    if output_format == OutputFormat.Suppress.value:
        return

    if query is None and output_format == OutputFormat.Table.value:
        query = default_table_query

    if query is None:
        output_json = result_json
    else:
        result = json.loads(result_json)
        output = jmespath.search(query, result)
        output_json = json.dumps(output)

    if output_format == OutputFormat.Json.value:
        click.echo(output_json)
    elif output_format == OutputFormat.Table.value:
        content = json.loads(output_json)
        if content is not None:
            columns = []
            rows = []

            if type(content) is dict:
                # single item
                item = content
                row = []
                for property_name in item:
                    columns.append(property_name)
                    row.append(item[property_name])
                rows.append(row)
            else:
                if len(content) == 0:
                    # nothing to output
                    return
                item = content[0]
                for property_name in item:
                    columns.append(property_name)
                for item in content:
                    row = []
                    for property_name in item:
                        row.append(item[property_name])
                    rows.append(row)

            click.echo(tabulate(rows, columns))
    else:
        raise click.ClickException(f"Unhandled output format: '{output_format}'")
