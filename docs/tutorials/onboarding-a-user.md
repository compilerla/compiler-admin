# Onboarding a New User

This tutorial demonstrates how to onboard a new user into the Compiler Google Workspace. The process involves creating their account and then assigning them the correct account type, such as "Staff" or "Contractor".

## 1. Create the User Account

The first step is to create the basic user account with the `user create` command. You need to provide a `username` for the new account (the part before `@compiler.la`).

The command will generate a random password and require the user to change it upon their first login.

You can also specify an email address with the `--notify` option to send the new account credentials to a manager or the user's personal email.

```bash
compiler-admin user create new_username --notify manager@compiler.la
```

This command creates the user, adds them to the default "team" group, and sends their temporary password to `manager@compiler.la`.

## 2. Set the Account Type

By default, new users may be placed in a default organizational unit (OU). The next step is to assign them to the correct one, which also manages their access and permissions. The `user convert` command is used for this.

Let's say we want to make this new user a full-time staff member.

```bash
compiler-admin user convert new_username staff
```

This command moves the user `new_username@compiler.la` into the "Staff" OU and adds them to the "staff" Google Group.

The available account types are:

- `staff`
- `partner`
- `contractor`

After these two steps, the new user is fully onboarded and ready to go.
