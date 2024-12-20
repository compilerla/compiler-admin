from argparse import Namespace
import pytest

from compiler_admin import RESULT_SUCCESS
from compiler_admin.commands.time.convert import (
    __name__ as MODULE,
    CONVERTERS,
    _get_source_converter,
    convert,
)
from compiler_admin.services.harvest import CONVERTERS as HARVEST_CONVERTERS
from compiler_admin.services.toggl import CONVERTERS as TOGGL_CONVERTERS


@pytest.fixture
def mock_get_source_converter(mocker):
    return mocker.patch(f"{MODULE}._get_source_converter")


@pytest.fixture
def mock_converters(mocker):
    return mocker.patch(f"{MODULE}.CONVERTERS", new={})


def test_get_source_converter_match(mock_converters):
    mock_converters["toggl"] = {"test_fmt": "converter"}
    result = _get_source_converter("toggl", "test_fmt")

    assert result == "converter"


def test_get_source_converter_mismatch():
    with pytest.raises(
        NotImplementedError, match="A converter for the given source and target formats does not exist: nope to toggl"
    ):
        _get_source_converter("nope", "toggl")
    with pytest.raises(
        NotImplementedError, match="A converter for the given source and target formats does not exist: toggl to nope"
    ):
        _get_source_converter("toggl", "nope")


def test_convert(mock_get_source_converter):
    args = Namespace(input="input", output="output", client="client", from_fmt="from", to_fmt="to")
    res = convert(args)

    assert res == RESULT_SUCCESS
    mock_get_source_converter.assert_called_once_with(args.from_fmt, args.to_fmt)
    mock_get_source_converter.return_value.assert_called_once_with(
        source_path=args.input, output_path=args.output, client_name=args.client
    )


def test_converters():
    assert CONVERTERS.get("harvest") == HARVEST_CONVERTERS
    assert CONVERTERS.get("toggl") == TOGGL_CONVERTERS
