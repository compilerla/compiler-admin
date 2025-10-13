import pytest

from compiler_admin.commands.time.verify import verify


@pytest.fixture(autouse=True)
def mock_environment(monkeypatch):
    monkeypatch.setenv("HARVEST_CLIENT_NAME", "Test_Client")
    monkeypatch.setenv("TOGGL_PROJECT_INFO", "notebooks/data/toggl-project-info-sample.json")
    monkeypatch.setenv("TOGGL_USER_INFO", "notebooks/data/toggl-user-info-sample.json")


def test_verify_one_file(cli_runner, harvest_file, toggl_file):
    """Test that verify works with a single harvest file."""
    for file in [harvest_file, toggl_file]:
        result = cli_runner.invoke(verify, [file])
        assert result.exit_code == 0
        assert f"Summary for: {file}" in result.output
        assert "Date range:" in result.output
        assert "Total entries:" in result.output
        assert "Total hours:" in result.output


def test_verify_two_files(cli_runner, harvest_file, toggl_file):
    """Test that verify works with two files."""
    result = cli_runner.invoke(verify, [harvest_file, toggl_file])
    assert result.exit_code == 0
    assert "Summaries match." in result.output


def test_verify_two_files_mismatched_details(cli_runner, tmp_path):
    """Test that verify shows detailed differences for mismatched files."""
    file1_content = """Date,Client,Project,Notes,Hours,First name,Last name
2025-01-01,ClientA,ProjectX,Note1,8.0,John,Doe
2025-01-01,ClientA,ProjectY,Note2,4.0,John,Doe
"""
    file2_content = """Date,Client,Project,Notes,Hours,First name,Last name
2025-01-01,ClientA,ProjectX,Note1,8.0,John,Doe
2025-01-01,ClientA,ProjectY,Note2,5.0,John,Doe
"""
    file1 = tmp_path / "file1.csv"
    file2 = tmp_path / "file2.csv"
    file1.write_text(file1_content)
    file2.write_text(file2_content)

    result = cli_runner.invoke(verify, [str(file1), str(file2)])
    assert result.exit_code == 1
    assert "Summaries do not match:" in result.output
    assert "- Total hours: 12.0 vs 13.0" in result.output
    assert "  Project 'ProjectY' hours: 4.0 vs 5.0" in result.output
    assert "  User 'John Doe', Project 'ProjectY' hours: 4.0 vs 5.0" in result.output


def test_verify_invalid_file_count(cli_runner, tmp_path):
    """Test that verify fails with an invalid number of files."""
    result = cli_runner.invoke(verify, [])
    assert result.exit_code == 0
    assert "Please provide one or two files to verify." in result.output

    f1 = tmp_path / "f1.csv"
    f2 = tmp_path / "f2.csv"
    f3 = tmp_path / "f3.csv"
    f1.touch()
    f2.touch()
    f3.touch()
    result = cli_runner.invoke(verify, [str(f1), str(f2), str(f3)])
    assert result.exit_code == 0
    assert "Please provide one or two files to verify." in result.output


def test_verify_unknown_file_type(cli_runner, tmp_path):
    """Test that verify fails with an unknown file type."""
    unknown_file = tmp_path / "unknown.csv"
    unknown_file.write_text("header1,header2\nvalue1,value2")
    result = cli_runner.invoke(verify, [str(unknown_file)])
    assert result.exit_code == 0
    assert "Error processing file" in result.output
