from importlib.metadata import version, PackageNotFoundError

RESULT_SUCCESS = 0
RESULT_FAILURE = 1

try:
    __version__ = version("compiler_admin")
except PackageNotFoundError:
    # package is not installed
    pass
