import os
from pathlib import Path
from shutil import rmtree
import subprocess

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.services.google import USER_ARCHIVE, CallGAMCommand


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

    res = CallGAMCommand(("config", "drive_dir", CONFIG_PATH_NAME, "verify"))
    res += CallGAMCommand(("create", "project"))
    res += CallGAMCommand(("oauth", "create"))
    res += CallGAMCommand(("user", admin_user, "check", "serviceaccount"))

    # download GYB installer to config directory
    gyb = CONFIG_PATH / "gyb-install.sh"
    with gyb.open("w+") as dest:
        res += subprocess.call(("curl", "-s", "-S", "-L", "https://gyb-shortn.jaylee.us/gyb-install"), stdout=dest)

    # install, giving values to options that prompt by default
    # https://github.com/GAM-team/got-your-back/blob/main/install-gyb.sh
    res += subprocess.call((gyb, "-u", admin_user, "-r", USER_ARCHIVE))

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
