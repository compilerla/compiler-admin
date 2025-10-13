# How to Convert a User's Account Type

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user convert` reference section](../../reference/cli/user.md#compiler-admin-user-convert).

This guide explains how to use the `compiler-admin user convert` command to change a user's account type.

This process moves the user between organizational units (OUs) and updates their group memberships (e.g., adding or removing them from the "Staff" or "Partners" groups).

## Basic Usage

To convert a user, you must provide their `username` and the target `account_type`.

```bash
compiler-admin user convert some.user staff
```

This command would convert `some.user@compiler.la` to a "Staff" account.

## Available Account Types

The following target account types are available:

- `staff`: For full-time staff members.
- `partner`: For partners of the company.
- `contractor`: For external contractors.
- `alumni`: For former employees. This is typically handled by the `offboard` command automatically.

## Forcing the Conversion

The command will ask for confirmation before proceeding. To bypass this, you can use the `--force` flag.

```bash
compiler-admin user convert some.user contractor --force
```

## Notifying on Conversion to Alumni

When converting a user to an `alumni` account, a new password is set. You can use the `--notify` option to send this new password to an email address.

```bash
compiler-admin user convert some.user alumni --notify their.personal@email.com
```
