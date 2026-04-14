from importlib.metadata import PackageNotFoundError, version


class Result:
    SUCCESS = 0
    FAILURE = 1


class Format:
    BASIC = 0
    CSV = 1
    JSON = 2


try:
    __version__ = version("compiler_admin")
except PackageNotFoundError:
    # package is not installed
    pass
