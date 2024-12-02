import json
from tempfile import NamedTemporaryFile
import pytest

import compiler_admin.services.files
from compiler_admin.services.files import JsonFileCache, pd, read_csv, read_json, write_csv, write_json


@pytest.fixture
def sample_data():
    return {"one": [2, 3, 4], "two": [4, 6, 8], "three": [6, 9, 12]}


@pytest.fixture
def sample_csv_lines(sample_data):
    one, two, three = sample_data["one"], sample_data["two"], sample_data["three"]
    expected_cols = list(sample_data.keys())

    # create CSV data from sample_data
    lines = [f"{','.join(expected_cols)}\n"]
    for i in range(len(one)):
        lines.append(f"{','.join([str(one[i]), str(two[i]), str(three[i])])}\n")

    return lines


@pytest.fixture
def spy_pandas(mocker):
    return mocker.patch.object(compiler_admin.services.files, "pd", wraps=pd)


@pytest.fixture
def temp_file():
    temp = NamedTemporaryFile()

    yield temp

    if not temp.closed:
        temp.close()


def test_read_csv(sample_data, sample_csv_lines, spy_pandas, temp_file):
    one, two, three = sample_data["one"], sample_data["two"], sample_data["three"]
    expected_cols = list(sample_data.keys())

    with open(temp_file.name, "wt") as f:
        f.writelines(sample_csv_lines)

    df = read_csv(temp_file.name, usecols=expected_cols)

    spy_pandas.read_csv.assert_called_once_with(temp_file.name, usecols=expected_cols)

    assert df.columns.to_list() == expected_cols
    assert df["one"].to_list() == one
    assert df["two"].to_list() == two
    assert df["three"].to_list() == three


def test_read_json(sample_data, temp_file):
    with open(temp_file.name, "wt") as f:
        json.dump(sample_data, f)

    assert read_json(temp_file.name) == sample_data


def test_write_csv(sample_data, sample_csv_lines, mocker, temp_file):
    df = pd.DataFrame(data=sample_data)
    expected_columns = df.columns.to_list()
    spy_df = mocker.patch.object(df, "to_csv", wraps=df.to_csv)

    write_csv(temp_file.name, df, columns=expected_columns)

    spy_df.assert_called_once_with(temp_file.name, columns=expected_columns, index=False)

    with open(temp_file.name, "rt") as f:
        assert f.readlines() == sample_csv_lines


def test_write_json(sample_data, temp_file):
    write_json(temp_file.name, sample_data)

    with open(temp_file.name, "rt") as f:
        assert json.load(f) == sample_data


def test_JsonFileCache(monkeypatch):
    with NamedTemporaryFile("w") as temp:
        monkeypatch.setenv("INFO_FILE", temp.name)
        temp.write('{"key": "value"}')
        temp.seek(0)

        cache = JsonFileCache("INFO_FILE")

        assert cache._path.exists()
        assert "key" in cache
        assert cache.get("key") == "value"
        assert cache["key"] == "value"
        assert cache.get("other") is None
        assert cache["other"] is None

        cache["key"] = "other"
        assert cache.get("key") == "other"
        assert cache["key"] == "other"


def test_JsonFileCache_no_file():
    cache = JsonFileCache("INFO_FILE")

    assert cache._cache == {}
    assert cache._path is None
    assert cache.get("key") is None
    assert "key" not in cache
