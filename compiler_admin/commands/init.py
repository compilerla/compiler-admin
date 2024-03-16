from argparse import Namespace
import os
from pathlib import Path
from shutil import rmtree
import subprocess

from compiler_admin.commands import RESULT_FAILURE, RESULT_SUCCESS
from compiler_admin.services.google import USER_ARCHIVE, CallGAMCommand


GAM_CONFIG_DIR = os.environ.get("GAMCFGDIR", "./.config/gam")
GAM_CONFIG_PATH = Path(GAM_CONFIG_DIR)
GYB_CONFIG_PATH = GAM_CONFIG_PATH.parent / "gyb"


def _clean_config_dir(config_dir: Path) -> None:
    config_dir.mkdir(parents=True, exist_ok=True)
    for path in config_dir.glob("**/*"):
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            rmtree(path)


def init(args: Namespace) -> int:
    """Initialize a new GAM project.

    See https://github.com/taers232c/GAMADV-XTD3/wiki/How-to-Install-Advanced-GAM

    Args:
        username (str): The Compiler admin with which to initialize a new project.

        gam (bool): If True, initialize a new GAM project.

        gyb (bool): If True, initialize a new GYB project.

    Returns:
        A value indicating if the operation succeeded or failed.
    """
    if not hasattr(args, "username"):
        raise ValueError("username is required")

    admin_user = args.username
    res = RESULT_SUCCESS

    if getattr(args, "gam", False):
        _clean_config_dir(GAM_CONFIG_PATH)
        # GAM is already installed via pyproject.toml
        res += CallGAMCommand(("config", "drive_dir", str(GAM_CONFIG_PATH), "verify"))
        res += CallGAMCommand(("create", "project"))
        res += CallGAMCommand(("oauth", "create"))
        res += CallGAMCommand(("user", admin_user, "check", "serviceaccount"))

    if getattr(args, "gyb", False):
        _clean_config_dir(GYB_CONFIG_PATH)
        # download GYB installer to config directory
        gyb = GYB_CONFIG_PATH / "gyb-install.sh"
        with gyb.open("w+") as dest:
            res += subprocess.call(("curl", "-s", "-S", "-L", "https://gyb-shortn.jaylee.us/gyb-install"), stdout=dest)

        res += subprocess.call(("chmod", "+x", str(gyb.absolute())))

        # install, giving values to some options
        # https://github.com/GAM-team/got-your-back/blob/main/install-gyb.sh
        #
        # use GYB_CONFIG_PATH.parent for the install directory option, otherwise we get a .config/gyb/gyb directory structure
        res += subprocess.call((gyb, "-u", admin_user, "-r", USER_ARCHIVE, "-d", str(GYB_CONFIG_PATH.parent)))

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
