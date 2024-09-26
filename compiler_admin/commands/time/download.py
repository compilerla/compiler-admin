from argparse import Namespace

from compiler_admin import RESULT_SUCCESS
from compiler_admin.services.toggl import INPUT_COLUMNS as TOGGL_COLUMNS, download_time_entries


def download(args: Namespace, *extras):
    params = dict(start_date=args.start, end_date=args.end, output_path=args.output, output_cols=TOGGL_COLUMNS)

    if args.client_ids:
        params.update(dict(client_ids=args.client_ids))
    if args.project_ids:
        params.update(dict(project_ids=args.project_ids))
    if args.task_ids:
        params.update(dict(task_ids=args.task_ids))
    if args.user_ids:
        params.update(dict(user_ids=args.user_ids))

    download_time_entries(**params)

    return RESULT_SUCCESS
