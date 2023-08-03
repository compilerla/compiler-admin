from compiler_admin import __version__ as version
from compiler_admin.services.google import CallGAMCommand


def info() -> int:
    """Print information about this package and the GAM environment.

    Returns:
        A value indicating if the operation succeeded or failed.
    """
    print(f"compiler-admin: {version}")

    CallGAMCommand(("version",))

    return CallGAMCommand(("info", "domain"))
