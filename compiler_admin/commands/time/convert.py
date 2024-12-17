from argparse import Namespace

from compiler_admin import RESULT_SUCCESS
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


def convert(args: Namespace, *extras):
    converter = _get_source_converter(args.from_fmt, args.to_fmt)

    converter(source_path=args.input, output_path=args.output, client_name=args.client)

    return RESULT_SUCCESS
