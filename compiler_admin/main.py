from compiler_admin.services.google import CallGAMCommand


def main():
    print("compiler-admin")

    return CallGAMCommand(["version"])


if __name__ == "__main__":
    raise SystemExit(main())
