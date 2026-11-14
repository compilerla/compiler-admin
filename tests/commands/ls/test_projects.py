import pytest

from compiler_admin import Result
from compiler_admin.api.toggl import TogglWorkspace
from compiler_admin.commands.ls.projects import projects


@pytest.fixture
def mock_toggl_projects(mocker):
    return mocker.patch("compiler_admin.commands.ls.projects.TogglUtils").return_value


def test_projects(cli_runner, mock_toggl_projects):
    mock_toggl_projects.get_projects.return_value = [
        {"id": 11, "name": "Project A", "client_id": 1, "active": True, "billable": False, "private": False}
    ]

    result = cli_runner.invoke(
        projects,
        ["--client-id", "1", "--id", "11", "--name", "Project A", "--active", "--internal"],
    )

    assert result.exit_code == Result.SUCCESS
    mock_toggl_projects.get_projects.assert_called_once_with(
        client_ids=[1],
        ids=[11],
        is_active=True,
        is_billable=False,
        is_private=True,
        name="Project A",
    )
    assert "Project A" in result.output


@pytest.fixture
def mock_workspace_get_projects(mocker):
    """Mock TogglWorkspace.get_projects for detailed output.

    The service calls response.json(), so we need a mock that returns
    a list when .json() is called.
    """
    mock_projects = [
        {
            "id": 123,
            "name": "Test Project",
            "client_id": 456,
            "client_name": "Test Client",
            "currency": "USD",
            "status": "active",
            "active": True,
            "billable": True,
            "is_private": False,
            "rate": 150.0,
            "estimated_hours": 100.0,
            "estimated_seconds": 360000,
            "actual_hours": 50.0,
            "actual_seconds": 180000,
            "fixed_fee": 15000.0,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "workspace_id": 789,
            "created_at": "2024-01-01T00:00:00Z",
        },
    ]
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_projects
    mock = mocker.patch.object(TogglWorkspace, "get_projects")
    mock.return_value = mock_response
    return mock


@pytest.fixture
def mock_workspace_get_projects_empty(mocker):
    """Mock TogglWorkspace.get_projects returning empty list."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = []
    mock = mocker.patch.object(TogglWorkspace, "get_projects")
    mock.return_value = mock_response
    return mock


def test_projects_detailed(cli_runner, mock_workspace_get_projects):
    result = cli_runner.invoke(projects, ["--detailed"])

    assert result.exit_code == Result.SUCCESS
    assert "id" in result.output
    assert "client_name" in result.output
    assert "currency" in result.output
    assert "rate" in result.output
    assert "estimated_hours" in result.output
    assert "Test Project" in result.output
    assert "Test Client" in result.output
    assert "150.0" in result.output


def test_projects_detailed_empty(cli_runner, mock_workspace_get_projects_empty):
    result = cli_runner.invoke(projects, ["--detailed"])

    assert result.exit_code == Result.SUCCESS
    mock_workspace_get_projects_empty.assert_called_once()


def test_projects_basic_no_detailed(cli_runner, mocker):
    """Verify that --detailed flag is NOT used when running basic projects."""
    # The basic path uses TogglUtils.get_projects (Reports API), not Track API.
    # Mock it so we don't hit the network.
    mock_utils = mocker.patch("compiler_admin.commands.ls.projects.TogglUtils").return_value
    mock_utils.get_projects.return_value = [{"id": 1, "name": "Mock Project"}]

    result = cli_runner.invoke(projects, [])

    assert result.exit_code == Result.SUCCESS
    mock_utils.get_projects.assert_called_once()


def test_projects_detailed_with_filter(cli_runner, mock_workspace_get_projects):
    result = cli_runner.invoke(projects, ["--detailed", "--name", "Test"])

    assert result.exit_code == Result.SUCCESS
    # Verify the name filter was passed to get_projects
    call_kwargs = mock_workspace_get_projects.call_args
    assert call_kwargs[1].get("name") == "Test"
