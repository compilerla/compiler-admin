from argparse import Namespace

from compiler_admin import RESULT_SUCCESS
from compiler_admin.services.toggl import INPUT_COLUMNS as TOGGL_COLUMNS, download_time_entries


def download(args: Namespace, *extras):
    download_time_entries(args.start, args.end, args.output, TOGGL_COLUMNS)

    return RESULT_SUCCESS
