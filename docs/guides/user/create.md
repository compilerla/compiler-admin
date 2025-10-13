# How to Create a New User

!!! seealso "Full Command Reference"

    For a complete reference of all options, see the [`compiler-admin user create` reference section](../../reference/cli/user.md#compiler-admin-user-create).

This guide explains how to use the `compiler-admin user create` command to create a new user account in the Compiler Google Workspace.

## Basic Usage

To create a new user, you must provide a `username` (the part of the email address before `@compiler.la`).

```bash
compiler-admin user create new.user
```

This creates the user `new.user@compiler.la`. The command generates a random temporary password and requires the user to change it on their first login.

## Notifying a Manager

You can send the new user's credentials to a manager or their personal email address using the `--notify` option.

```bash
compiler-admin user create new.user --notify manager@compiler.la
```

## Passing Additional Options to GAM

The `compiler-admin user create` command is a wrapper around the powerful `gam create user` command. You can pass additional arguments directly to GAM to specify more details about the user, such as their first and last name.

For example, to create a user and set their name:

```bash
compiler-admin user create new.user firstname "New" lastname "User"
```

For a full list of the available options you can pass through to GAM, please refer to the [GAM7 documentation on creating users](https://github.com/GAM-team/GAM/wiki/Users#create-a-user).
