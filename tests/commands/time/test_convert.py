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


def test_convert(cli_runner, mock_get_source_converter):
    result = cli_runner.invoke(
        convert, ["--input", "input", "--output", "output", "--client", "client", "--from", "harvest", "--to", "toggl"]
    )

    assert result.exit_code == RESULT_SUCCESS
    mock_get_source_converter.assert_called_once_with("harvest", "toggl")
    mock_get_source_converter.return_value.assert_called_once_with(
        source_path="input", output_path="output", client_name="client"
    )


def test_converters():
    assert CONVERTERS.get("harvest") == HARVEST_CONVERTERS
    assert CONVERTERS.get("toggl") == TOGGL_CONVERTERS
