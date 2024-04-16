from compiler_admin import __version__ as version, RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.services.google import CallGAMCommand, CallGYBCommand


def info() -> int:
    """Print information about this package and the GAM environment.

    Returns:
        A value indicating if the operation succeeded or failed.
    """
    print(f"compiler-admin: {version}")

    res = CallGAMCommand(("version",))
    res += CallGAMCommand(("info", "domain"))
    res += CallGYBCommand(("--version",))

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
