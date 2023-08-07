from compiler_admin.commands import RESULT_SUCCESS, RESULT_FAILURE
from compiler_admin.services.google import (
    GROUP_PARTNERS,
    GROUP_STAFF,
    OU_CONTRACTORS,
    OU_PARTNERS,
    OU_STAFF,
    add_user_to_group,
    move_user_ou,
    remove_user_from_group,
    user_account_name,
    user_exists,
    user_is_partner,
    user_is_staff,
)


ACCOUNT_TYPE_OU = {"contractor": OU_CONTRACTORS, "partner": OU_PARTNERS, "staff": OU_STAFF}


def convert(username: str, account_type: str) -> int:
    f"""Convert a user of one type to another.
    Args:
        username (str): The account to convert. Must exist already.

        account_type (str): One of {", ".join(ACCOUNT_TYPE_OU.keys())}
    Returns:
        A value indicating if the operation succeeded or failed.
    """
    account = user_account_name(username)

    if not user_exists(account):
        print(f"User does not exist: {account}")
        return RESULT_FAILURE

    if account_type not in ACCOUNT_TYPE_OU:
        print(f"Unknown account type for conversion: {account_type}")
        return RESULT_FAILURE

    print(f"User exists, converting to: {account_type} for {account}")
    res = RESULT_SUCCESS

    if account_type == "contractor":
        if user_is_partner(account):
            res += remove_user_from_group(account, GROUP_PARTNERS)
            res += remove_user_from_group(account, GROUP_STAFF)
        elif user_is_staff(account):
            res = remove_user_from_group(account, GROUP_STAFF)

    elif account_type == "staff":
        if user_is_partner(account):
            res += remove_user_from_group(account, GROUP_PARTNERS)
        elif user_is_staff(account):
            print(f"User is already staff: {account}")
            return RESULT_FAILURE
        res += add_user_to_group(account, GROUP_STAFF)

    elif account_type == "partner":
        if user_is_partner(account):
            print(f"User is already partner: {account}")
            return RESULT_FAILURE
        if not user_is_staff(account):
            res += add_user_to_group(account, GROUP_STAFF)
        res += add_user_to_group(account, GROUP_PARTNERS)

    res += move_user_ou(account, ACCOUNT_TYPE_OU[account_type])

    print(f"Account conversion complete for: {account}")

    return RESULT_SUCCESS if res == RESULT_SUCCESS else RESULT_FAILURE
