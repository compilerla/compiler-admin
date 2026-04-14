import json
import os
from io import TextIOBase
from pathlib import Path
from typing import TextIO

import pandas as pd


def read_csv(file_path, **kwargs) -> pd.DataFrame:
    """Read a file path or buffer of CSV data into a pandas.DataFrame."""
    return pd.read_csv(file_path, **kwargs)


def read_json(file_path):
    """Read a file path of JSON data into a python object."""

    if isinstance(file_path, (str, Path)):
        with open(file_path, "r") as f:
            return json.load(f)
    elif isinstance(file_path, (TextIOBase, TextIO)):
        return json.load(file_path)
    else:
        raise NotImplementedError(f"Input type for file_path not allowed: {type(file_path)}")


def write_csv(file_path, data: pd.DataFrame, columns: list[str] = None):
    """Write a pandas.DataFrame as CSV to the given path or buffer, with an optional list of columns to write."""
    data.to_csv(file_path, columns=columns, index=False)


def write_json(file_path, data):
    """Write a python object as JSON to the given path."""
    if isinstance(file_path, (str, Path)):
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    elif isinstance(file_path, (TextIOBase, TextIO)):
        json.dump(data, file_path, indent=2)
    else:
        raise NotImplementedError(f"Input type for file_path not allowed: {type(file_path)}")


class JsonFileCache:
    """Very basic in-memory cache of a JSON file."""

    def __init__(self, env_file_path=None):
        self._cache = {}
        self._path = None

        if env_file_path:
            p = os.environ.get(env_file_path)
            self._path = Path(p) if p else None
        if self._path and self._path.exists():
            self._cache.update(read_json(self._path))

    def __contains__(self, key):
        return key in self._cache

    def __getitem__(self, key):
        return self._cache.get(key)

    def __setitem__(self, key, value):
        self._cache[key] = value

    def get(self, key, default=None):
        return self._cache.get(key, default)
