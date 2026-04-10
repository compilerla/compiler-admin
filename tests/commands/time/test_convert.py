import pytest

from compiler_admin import Result
from compiler_admin.commands.time.convert import TIME_SERVICES, __name__ as MODULE, _get_source_converter, convert
from compiler_admin.services.harvest import HarvestTime
from compiler_admin.services.toggl import TogglTime


@pytest.fixture
def mock_get_source_converter(mocker):
    return mocker.patch(f"{MODULE}._get_source_converter")


@pytest.fixture
def mock_time_services(mocker):
    return mocker.patch(f"{MODULE}.TIME_SERVICES", new={})


def test_get_source_converter_match(mocker, mock_time_services):
    mock_time_services["toggl"] = mocker.Mock(converters={"test_fmt": "converter"})
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

    assert result.exit_code == Result.SUCCESS
    mock_get_source_converter.assert_called_once_with("harvest", "toggl")
    mock_get_source_converter.return_value.assert_called_once_with(
        source_path="input", output_path="output", client_name="client"
    )


@pytest.mark.parametrize("service,service_type", (("harvest", HarvestTime), ("toggl", TogglTime)))
def test_services(service, service_type):
    assert isinstance(TIME_SERVICES.get(service), service_type)
