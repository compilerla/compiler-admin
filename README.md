# Compiler Admin

Automating Compiler's administrative tasks.

Built on top of [GAMADV-XTD3](https://github.com/taers232c/GAMADV-XTD3) and [GYB](https://github.com/GAM-team/got-your-back).

**Note:** This tool can only be used by those with administrator access to Compiler's Google Workspace.

## Usage

```bash
$ compiler-admin -h
usage: compiler-admin [-h] [-v] {info,init,create,convert,delete,offboard,reset-password,restore,signout} ...

positional arguments:
  {info,init,create,convert,delete,offboard,reset-password,restore,signout}
    info                Print configuration and debugging information.
    init                Initialize a new admin project. This command should be run once before any others.
    create              Create a new user in the Compiler domain.
    convert             Convert a user account to a new type.
    delete              Delete a user account.
    offboard            Offboard a user account.
    reset-password      Reset a user's password to a randomly generated string.
    restore             Restore an email backup from a prior offboarding.
    signout             Signs a user out from all active sessions.

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

## Getting started

```bash
git clone https://github.com/compilerla/compiler-admin.git

cd compiler-admin
```

Now open in VS Code, and when prompted, reopen in the devcontainer.

## Initial setup

Initial setup of a GAMADV-XTD3 project and GYB project is required to provide necessary API access to the Google Workspace.

```bash
$ compiler-admin init -h
usage: compiler-admin init [-h] [--gam] [--gyb] username

positional arguments:
  username    A Compiler user account name, sans domain.

options:
  -h, --help  show this help message and exit
  --gam       If provided, initialize a new GAM project.
  --gyb       If provided, initialize a new GYB project.
```

The `init` commands follows the steps in the [GAMADV-XTD3 Wiki](https://github.com/taers232c/GAMADV-XTD3/wiki/#requirements).

Additionally, GYB is used for Gmail backup/restore. See the [GYB Wiki](https://github.com/GAM-team/got-your-back/wiki) for more information.

## Creating a user

```bash
$ compiler-admin create -h
usage: compiler-admin create [-h] [--notify NOTIFY] username

positional arguments:
  username         A Compiler user account name, sans domain.

options:
  -h, --help       show this help message and exit
  --notify NOTIFY  An email address to send the newly created account info.
```

Additional options are passed through to GAM, see more about [GAM user create](https://github.com/taers232c/GAMADV-XTD3/wiki/Users#create-a-user)

## Convert a user

```bash
$ compiler-admin convert -h
usage: compiler-admin convert [-h] username {contractor,partner,staff}

positional arguments:
  username              A Compiler user account name, sans domain.
  {contractor,partner,staff}
                        Target account type for this conversion.

options:
  -h, --help            show this help message and exit
```

## Offboarding a user

```bash
$ compiler-admin offboard -h
usage: compiler-admin offboard [-h] [--alias ALIAS] [--force] username

positional arguments:
  username       A Compiler user account name, sans domain.

options:
  -h, --help     show this help message and exit
  --alias ALIAS  Account to assign username as an alias.
  --force        Don't ask for confirmation before offboarding.
```

This script creates a local backup of `USER`'s inbox, see [Restore](#restore-an-email-backup)

## Restore an email backup

Retore a backup from a prior [Offboarding](#offboarding-a-user) into the `archive@compiler.la` account.

```bash
$ compiler-admin restore -h
usage: compiler-admin restore [-h] username

positional arguments:
  username    The user's account name, sans domain.

options:
  -h, --help  show this help message and exit
```
