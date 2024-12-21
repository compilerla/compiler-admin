import os
from pathlib import Path
from shutil import rmtree
import subprocess

import click

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


@click.command()
@click.option("--gam", "init_gam", is_flag=True)
@click.option("--gyb", "init_gyb", is_flag=True)
@click.argument("username")
def init(username: str, init_gam: bool = False, init_gyb: bool = False):
    """Initialize a new GAM and/or GYB project.

    See:

    - https://github.com/taers232c/GAMADV-XTD3/wiki/How-to-Install-Advanced-GAM
    - https://github.com/GAM-team/got-your-back/wiki
    """
    if init_gam:
        _clean_config_dir(GAM_CONFIG_PATH)
        # GAM is already installed via pyproject.toml
        CallGAMCommand(("config", "drive_dir", str(GAM_CONFIG_PATH), "verify"))
        CallGAMCommand(("create", "project"))
        CallGAMCommand(("oauth", "create"))
        CallGAMCommand(("user", username, "check", "serviceaccount"))

    if init_gyb:
        _clean_config_dir(GYB_CONFIG_PATH)
        # download GYB installer to config directory
        gyb = GYB_CONFIG_PATH / "gyb-install.sh"
        with gyb.open("w+") as dest:
            subprocess.call(("curl", "-s", "-S", "-L", "https://gyb-shortn.jaylee.us/gyb-install"), stdout=dest)

        subprocess.call(("chmod", "+x", str(gyb.absolute())))

        # install, giving values to some options
        # https://github.com/GAM-team/got-your-back/blob/main/install-gyb.sh
        #
        # use GYB_CONFIG_PATH.parent for the install directory option, otherwise we get a .config/gyb/gyb directory structure
        subprocess.call((gyb, "-u", username, "-r", USER_ARCHIVE, "-d", str(GYB_CONFIG_PATH.parent)))
