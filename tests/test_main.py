import subprocess

from compiler_admin.main import main

import pytest


@pytest.fixture
def main_cmd():
    return "compiler-admin"


def test_main(capfd, main_cmd):
    res = main(argv=[])
    captured = capfd.readouterr()

    assert res == 0
    assert main_cmd in captured.out
    assert "GAMADV-XTD3" in captured.out
    assert "WARNING: Config File:" not in captured.err


def test_run_compiler(capfd, main_cmd):
    # call CLI command as a subprocess
    res = subprocess.call([main_cmd])
    captured = capfd.readouterr()

    assert res == 0
    assert main_cmd in captured.out
    assert "GAMADV-XTD3" in captured.out
    assert "WARNING: Config File:" not in captured.err
