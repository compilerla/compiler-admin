import math
import sys
from datetime import date, datetime, timedelta
from io import BytesIO, StringIO
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
import pytest

import compiler_admin.services.toggl
from compiler_admin.services.toggl import __name__ as MODULE, TogglTime, files


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    monkeypatch.setenv("HARVEST_CLIENT_NAME", "Test_Client")
    monkeypatch.setenv("TOGGL_PROJECT_INFO", "notebooks/data/toggl-project-info-sample.json")
    monkeypatch.setenv("TOGGL_USER_INFO", "notebooks/data/toggl-user-info-sample.json")


@pytest.fixture
def spy_files(mocker):
    return mocker.patch.object(compiler_admin.services.toggl, "files", wraps=files)


@pytest.fixture()
def mock_user_info(mocker):
    return mocker.patch.object(TogglTime, "user_info")


@pytest.fixture
def mock_google_user_info(mocker):
    return mocker.patch(f"{MODULE}.google_user_info")


@pytest.fixture
def mock_toggl_api_env(monkeypatch):
    monkeypatch.setenv("TOGGL_API_TOKEN", "token")
    monkeypatch.setenv("TOGGL_CLIENT_ID", "1234")
    monkeypatch.setenv("TOGGL_WORKSPACE_ID", "workspace")


class TestTogglTime:

    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.time = TogglTime()
        self.time.api = mocker.Mock()

    @pytest.fixture
    def mock_toggl_detailed_time_entries(self, toggl_file):
        mock_csv_bytes = Path(toggl_file).read_bytes()
        self.time.api.detailed_time_entries.return_value.content = mock_csv_bytes
        return self.time.api.detailed_time_entries

    def test_get_first_name_matching(self, mock_user_info):
        mock_user_info.return_value = {"email": {"First Name": "User"}}

        result = self.time._get_first_name("email")

        assert result == "User"

    def test_get_first_name_lookup_with_record(self, mock_user_info, mock_google_user_info):
        email = "user@email.com"
        mock_user_info.return_value = {email: {"Data": 1234}}
        mock_google_user_info.return_value = {"First Name": "User"}

        result = self.time._get_first_name(email)

        assert result == "User"
        assert mock_user_info.return_value[email]["First Name"] == "User"
        assert mock_user_info.return_value[email]["Data"] == 1234
        mock_google_user_info.assert_called_once_with(email)

    def test_get_first_name_lookup_without_record(self, mock_user_info, mock_google_user_info):
        email = "user@email.com"
        mock_user_info.return_value = {email: {}}
        mock_google_user_info.return_value = {"First Name": "User"}

        result = self.time._get_first_name(email)

        assert result == "User"
        assert mock_user_info.return_value[email]["First Name"] == "User"
        assert list(mock_user_info.return_value[email].keys()) == ["First Name"]
        mock_google_user_info.assert_called_once_with(email)

    def test_get_last_name_matching(self, mock_user_info, mock_google_user_info):
        mock_user_info.return_value = {"email": {"Last Name": "User"}}

        result = self.time._get_last_name("email")

        assert result == "User"
        mock_google_user_info.assert_not_called()

    def test_get_last_name_lookup_with_record(self, mock_user_info, mock_google_user_info):
        email = "user@email.com"
        mock_user_info.return_value = {email: {"Data": 1234}}
        mock_google_user_info.return_value = {"Last Name": "User"}

        result = self.time._get_last_name(email)

        assert result == "User"
        assert mock_user_info.return_value[email]["Last Name"] == "User"
        assert mock_user_info.return_value[email]["Data"] == 1234
        mock_google_user_info.assert_called_once_with(email)

    def test_get_last_name_lookup_without_record(self, mock_user_info, mock_google_user_info):
        email = "user@email.com"
        mock_user_info.return_value = {email: {}}
        mock_google_user_info.return_value = {"Last Name": "User"}

        result = self.time._get_last_name(email)

        assert result == "User"
        assert mock_user_info.return_value[email]["Last Name"] == "User"
        assert list(mock_user_info.return_value[email].keys()) == ["Last Name"]
        mock_google_user_info.assert_called_once_with(email)

    def test_str_timedelta(self):
        dt = "01:30:15"

        result = self.time._str_timedelta(dt)

        assert isinstance(result, timedelta)
        assert result.total_seconds() == (1 * 60 * 60) + (30 * 60) + 15

    @pytest.mark.usefixtures("mock_google_user_info")
    def test_prepare_input(self, toggl_file, spy_files):
        df = self.time._prepare_input(toggl_file)

        spy_files.read_csv.assert_called_once()
        call_args = spy_files.read_csv.call_args
        assert (toggl_file,) in call_args
        assert call_args.kwargs["usecols"] == TogglTime.TOGGL_COLUMNS
        assert call_args.kwargs["parse_dates"] == ["Start date"]
        assert call_args.kwargs["cache_dates"] is True

        df_cols = df.columns.to_list()

        assert "First name" in df_cols
        assert "Last name" in df_cols
        assert df["Start date"].dtype.name == "datetime64[us]"
        assert df["Start time"].dtype.name == "timedelta64[us]"
        assert df["Duration"].dtype.name == "timedelta64[us]"
        assert df["Hours"].dtype.name == "float64"

        df = self.time._prepare_input(toggl_file, column_renames={"Start date": "SD", "Start time": "ST", "Duration": "D"})

        assert "Start date" not in df.columns
        assert "Start time" not in df.columns
        assert "Duration" not in df.columns
        assert df["SD"].dtype.name == "datetime64[us]"
        assert df["ST"].dtype.name == "timedelta64[us]"
        assert df["D"].dtype.name == "timedelta64[us]"

    def test_converters(self):
        assert self.time.converters.get("harvest") == self.time.convert_to_harvest
        assert self.time.converters.get("justworks") == self.time.convert_to_justworks
        assert self.time.converters.get("nope") is None

    def test_convert_to_harvest_mocked(self, toggl_file, spy_files, mock_google_user_info):
        mock_google_user_info.return_value = {}

        self.time.convert_to_harvest(toggl_file, client_name=None)

        spy_files.write_csv.assert_called_once()
        call_args = spy_files.write_csv.call_args
        assert sys.stdout in call_args[0]
        assert call_args.kwargs["columns"] == TogglTime.HARVEST_COLUMNS

    def test_convert_to_harvest_sample(self, toggl_file, harvest_file, mock_google_user_info):
        mock_google_user_info.return_value = {}
        output = None

        with StringIO() as output_data:
            self.time.convert_to_harvest(toggl_file, output_data, client_name="Test Client 123")
            output = output_data.getvalue()

        assert output
        assert isinstance(output, str)
        assert ",".join(TogglTime.HARVEST_COLUMNS) in output

        order = ["Date", "First name", "Hours"]
        sample_output_df = pd.read_csv(harvest_file).sort_values(order)
        output_df = pd.read_csv(StringIO(output)).sort_values(order)

        assert set(output_df.columns.to_list()) <= set(sample_output_df.columns.to_list())
        assert output_df["Client"].eq("Test Client 123").all()

    def test_convert_to_harvest_with_duplicates(self, mock_google_user_info):
        # Test that seemingly duplicate time entries are disambiguated

        mock_google_user_info.return_value = {"First Name": "Test", "Last Name": "User"}
        csv_input = """Email,Project,Task,Client,Start date,Start time,Duration,Description
    test@example.com,Compiler,Backend,ACME,2025-11-18,09:00:00,01:00:00,A task
    test@example.com,Compiler,Backend,ACME,2025-11-18,10:00:00,01:00:00,A task
    test@example.com,Compiler,Backend,ACME,2025-11-18,11:00:00,02:00:00,Another task
    """
        input_buffer = StringIO(csv_input)
        output_buffer = StringIO()

        self.time.convert_to_harvest(source_path=input_buffer, output_path=output_buffer, client_name="ACME")

        output_buffer.seek(0)
        df = pd.read_csv(output_buffer)

        assert df.loc[0, "Notes"] == "[Backend] A task (1/2)"
        assert df.loc[1, "Notes"] == "[Backend] A task (2/2)"
        assert df.loc[2, "Notes"] == "[Backend] Another task"

    def test_convert_to_justworks_mocked(self, toggl_file, spy_files):
        self.time.convert_to_justworks(toggl_file)

        spy_files.write_csv.assert_called_once()
        call_args = spy_files.write_csv.call_args
        assert sys.stdout in call_args[0]
        assert call_args.kwargs["columns"] == TogglTime.JUSTWORKS_COLUMNS

    def test_convert_to_justworks_sample(self, toggl_file, justworks_file):
        output = None

        with StringIO() as output_data:
            self.time.convert_to_justworks(toggl_file, output_data)
            output = output_data.getvalue()

        assert output
        assert isinstance(output, str)
        assert ",".join(TogglTime.JUSTWORKS_COLUMNS) in output

        order = ["Start Date", "First Name", "Regular Hours"]
        sample_output_df = pd.read_csv(justworks_file).sort_values(order)
        output_df = pd.read_csv(StringIO(output)).sort_values(order)

        assert set(output_df.columns.to_list()) <= set(sample_output_df.columns.to_list())
        assert output_df.shape == sample_output_df.shape

    @pytest.mark.usefixtures("mock_toggl_api_env", "mock_toggl_detailed_time_entries")
    def test_download(self, toggl_file):
        dt = datetime.now()
        mock_csv_bytes = Path(toggl_file).read_bytes()

        with NamedTemporaryFile("w") as temp:
            self.time.download(dt, dt, temp.name)
            temp.flush()
            response_csv_bytes = Path(temp.name).read_bytes()

            # load each CSV into a DataFrame
            mock_df = pd.read_csv(BytesIO(mock_csv_bytes))
            response_df = pd.read_csv(BytesIO(response_csv_bytes))

            # check that the response DataFrame has all columns from the mock DataFrame
            assert set(response_df.columns.to_list()).issubset(mock_df.columns.to_list())

            # check that all column values from response DataFrame are the same
            # as corresponding column values from the mock DataFrame
            for col in response_df.columns:
                assert response_df[col].equals(mock_df[col])

    @pytest.mark.usefixtures("mock_toggl_api_env")
    def test_lock(self):
        lock_date = datetime(2025, 10, 11)
        self.time.lock(lock_date)

        self.time.api.update_workspace_preferences.assert_called_once_with(report_locked_at="2025-10-11")

    def test_summarize(self, toggl_file):
        """Test that summarize returns a valid TimeSummary object."""
        summary = self.time.summarize(toggl_file)

        assert summary.earliest_date == date(2023, 1, 2)
        assert summary.latest_date == date(2023, 1, 30)
        assert summary.total_rows == 250
        assert math.isclose(summary.total_hours, 518.32, rel_tol=1e-5)
        assert len(summary.hours_per_project) > 0
        assert len(summary.hours_per_user_project) > 0
