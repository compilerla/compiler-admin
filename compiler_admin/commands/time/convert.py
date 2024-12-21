import os
import sys
from typing import TextIO

import click

from compiler_admin.services.harvest import CONVERTERS as HARVEST_CONVERTERS
from compiler_admin.services.toggl import CONVERTERS as TOGGL_CONVERTERS


CONVERTERS = {"harvest": HARVEST_CONVERTERS, "toggl": TOGGL_CONVERTERS}


def _get_source_converter(from_fmt: str, to_fmt: str):
    from_fmt = from_fmt.lower().strip() if from_fmt else ""
    to_fmt = to_fmt.lower().strip() if to_fmt else ""
    converter = CONVERTERS.get(from_fmt, {}).get(to_fmt)

    if converter:
        return converter
    else:
        raise NotImplementedError(
            f"A converter for the given source and target formats does not exist: {from_fmt} to {to_fmt}"
        )


@click.command()
@click.option(
    "--input",
    default=os.environ.get("TOGGL_DATA", sys.stdin),
    help="The path to the source data for conversion. Defaults to $TOGGL_DATA or stdin.",
)
@click.option(
    "--output",
    default=os.environ.get("HARVEST_DATA", sys.stdout),
    help="The path to the file where converted data should be written. Defaults to $HARVEST_DATA or stdout.",
)
@click.option(
    "--from",
    "from_fmt",
    default="toggl",
    help="The format of the source data.",
    show_default=True,
    type=click.Choice(sorted(CONVERTERS.keys()), case_sensitive=False),
)
@click.option(
    "--to",
    "to_fmt",
    default="harvest",
    help="The format of the converted data.",
    show_default=True,
    type=click.Choice(sorted([to_fmt for sub in CONVERTERS.values() for to_fmt in sub.keys()]), case_sensitive=False),
)
@click.option("--client", help="The name of the client to use in converted data.")
def convert(
    input: str | TextIO = os.environ.get("TOGGL_DATA", sys.stdin),
    output: str | TextIO = os.environ.get("HARVEST_DATA", sys.stdout),
    from_fmt="toggl",
    to_fmt="harvest",
    client="",
):
    """
    Convert a time report from one format into another.
    """
    converter = _get_source_converter(from_fmt, to_fmt)

    click.echo(f"Converting data from format: {from_fmt} to format: {to_fmt}")

    converter(source_path=input, output_path=output, client_name=client)
