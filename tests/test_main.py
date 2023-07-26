import subprocess

from compiler_admin.main import main

import pytest


@pytest.fixture
def main_cmd():
    return "compiler-admin"


def test_main(capfd, main_cmd):
    main()
    captured = capfd.readouterr()

    assert main_cmd in captured.out


def test_run_compiler(capfd, main_cmd):
    # call CLI command as a subprocess
    subprocess.call([main_cmd])
    captured = capfd.readouterr()

    assert main_cmd in captured.out
