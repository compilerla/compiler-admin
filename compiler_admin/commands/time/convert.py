from argparse import Namespace

import pandas as pd

from compiler_admin import RESULT_SUCCESS
from compiler_admin.services.harvest import INPUT_COLUMNS as TOGGL_COLUMNS, convert_to_toggl
from compiler_admin.services.toggl import INPUT_COLUMNS as HARVEST_COLUMNS, convert_to_harvest


def _get_source_converter(source):
    columns = pd.read_csv(source, nrows=0).columns.tolist()

    if set(HARVEST_COLUMNS) <= set(columns):
        return convert_to_harvest
    elif set(TOGGL_COLUMNS) <= set(columns):
        return convert_to_toggl
    else:
        raise NotImplementedError("A converter for the given source data does not exist.")


def convert(args: Namespace, *extras):
    converter = _get_source_converter(args.input)

    converter(args.input, args.output, args.client)

    return RESULT_SUCCESS
