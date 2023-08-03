from compiler_admin import __version__ as version
from compiler_admin.services.google import CallGAMCommand


def main():
    print(f"compiler-admin: {version}")

    return CallGAMCommand(["version"])


if __name__ == "__main__":
    raise SystemExit(main())
