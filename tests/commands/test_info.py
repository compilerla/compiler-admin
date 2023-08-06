from compiler_admin import __version__ as version
from compiler_admin.commands import RESULT_SUCCESS
from compiler_admin.commands.info import info
from compiler_admin.services.google import DOMAIN


def test_info(capfd):
    res = info()
    captured = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert f"compiler-admin: {version}" in captured.out
    assert "GAMADV-XTD3" in captured.out
    assert f"Primary Domain: {DOMAIN}" in captured.out
    assert "Got Your Back" in captured.out
    assert "WARNING: Config File:" not in captured.err
