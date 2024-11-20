from argparse import Namespace
from io import StringIO
import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.time.convert import (
    __name__ as MODULE,
    _get_source_converter,
    convert_to_harvest,
    convert_to_toggl,
    convert,
)


@pytest.fixture
def mock_get_source_converter(mocker):
    return mocker.patch(f"{MODULE}._get_source_converter")


def test_get_source_converter_match_toggl(toggl_file):
    result = _get_source_converter(toggl_file)

    assert result == convert_to_harvest


def test_get_source_converter_match_harvest(harvest_file):
    result = _get_source_converter(harvest_file)

    assert result == convert_to_toggl


def test_get_source_converter_mismatch():
    data = StringIO("one,two,three\n1,2,3")

    with pytest.raises(NotImplementedError, match="A converter for the given source data does not exist."):
        _get_source_converter(data)


def test_convert(mock_get_source_converter):
    args = Namespace(input="input", output="output", client="client")
    res = convert(args)

    assert res == RESULT_SUCCESS
    mock_get_source_converter.assert_called_once_with(args.input)
    mock_get_source_converter.return_value.assert_called_once_with(
        source_path=args.input, output_path=args.output, client_name=args.client
    )
