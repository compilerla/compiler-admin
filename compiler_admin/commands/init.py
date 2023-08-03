import os
from pathlib import Path
from shutil import rmtree

from compiler_admin.commands import RESULT_SUCCESS
from compiler_admin.services.google import CallGAMCommand


CONFIG_DIR = os.environ.get("GAMCFGDIR", "./.config")
CONFIG_PATH = Path(CONFIG_DIR)
CONFIG_PATH_NAME = str(CONFIG_PATH)


def _clean_config_dir():
    for path in CONFIG_PATH.glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)


def init(admin_user: str) -> int:
    """Initialize a new GAM project.

    See https://github.com/taers232c/GAMADV-XTD3/wiki/How-to-Install-Advanced-GAM

    Args:
        admin_user (str): The Compiler admin with which to initialize a new project.
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    if CONFIG_PATH.exists():
        _clean_config_dir()

    CallGAMCommand(("config", "drive_dir", CONFIG_PATH_NAME, "verify"))
    CallGAMCommand(("create", "project"))
    CallGAMCommand(("oauth", "create"))
    CallGAMCommand(("user", admin_user, "check", "serviceaccount"))

    return RESULT_SUCCESS
