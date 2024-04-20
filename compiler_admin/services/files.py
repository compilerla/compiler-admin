import json

import pandas as pd


def read_csv(file_path, **kwargs) -> pd.DataFrame:
    """Read a file path or buffer of CSV data into a pandas.DataFrame."""
    return pd.read_csv(file_path, **kwargs)


def read_json(file_path: str):
    """Read a file path of JSON data into a python object."""
    with open(file_path, "r") as f:
        return json.load(f)


def write_csv(file_path, data: pd.DataFrame, columns: list[str] = None):
    """Write a pandas.DataFrame as CSV to the given path or buffer, with an optional list of columns to write."""
    data.to_csv(file_path, columns=columns, index=False)


def write_json(file_path: str, data):
    """Write a python object as JSON to the given path."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
