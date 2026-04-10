from importlib.metadata import PackageNotFoundError, version


class Result:
    SUCCESS = 0
    FAILURE = 1


try:
    __version__ = version("compiler_admin")
except PackageNotFoundError:
    # package is not installed
    pass
