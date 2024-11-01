# Compiler Admin

Automating Compiler's administrative tasks.

Built on top of [GAMADV-XTD3](https://github.com/taers232c/GAMADV-XTD3) and [GYB](https://github.com/GAM-team/got-your-back).

**Note:** This tool can only be used by those with administrator access to Compiler's Google Workspace.

## Usage

```bash
$ compiler-admin -h
usage: compiler-admin [-h] [-v] {info,init,time,user} ...

positional arguments:
  {info,init,time,user}
                        The command to run
    info                Print configuration and debugging information.
    init                Initialize a new admin project. This command should be run once before any others.
    time                Work with Compiler time entries.
    user                Work with users in the Compiler org.

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

## Working with time entires

The `time` command provides an interface for working with time entries from Compiler's various systems:

```bash
$ compiler-admin time -h
usage: compiler-admin time [-h] {convert,download} ...

positional arguments:
  {convert,download}  The time command to run.
    convert           Convert a time report from one format into another.
    download          Download a Toggl report in CSV format.

options:
  -h, --help          show this help message and exit
```

### Downloading a Toggl report

Use this command to download a time report from Toggl in CSV format:

```bash
$ compiler-admin time download -h
usage: compiler-admin time download [-h] [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--output OUTPUT]
                                    [--client CLIENT_ID] [--project PROJECT_ID] [--task TASK_ID] [--user USER_ID]

options:
  -h, --help            show this help message and exit
  --start YYYY-MM-DD    The start date of the reporting period. Defaults to the beginning of the prior month.
  --end YYYY-MM-DD      The end date of the reporting period. Defaults to the end of the prior month.
  --output OUTPUT       The path to the file where converted data should be written. Defaults to stdout.
  --client CLIENT_ID    An ID for a Toggl Client to filter for in reports. Can be supplied more than once.
  --project PROJECT_ID  An ID for a Toggl Project to filter for in reports. Can be supplied more than once.
  --task TASK_ID        An ID for a Toggl Project Task to filter for in reports. Can be supplied more than once.
  --user USER_ID        An ID for a Toggl User to filter for in reports. Can be supplied more than once.
```

### Converting an hours report

With a CSV exported from either Harvest or Toggl, use this command to convert to the opposite format:

```bash
$ compiler-admin time convert -h
usage: compiler-admin time convert [-h] [--input INPUT] [--output OUTPUT] [--client CLIENT]

options:
  -h, --help       show this help message and exit
  --input INPUT    The path to the source data for conversion. Defaults to stdin.
  --output OUTPUT  The path to the file where converted data should be written. Defaults to stdout.
  --client CLIENT  The name of the client to use in converted data.
```

## Working with users

The following commands are available to work with users in the Compiler domain:

```bash
$ compiler-admin user -h
usage: compiler-admin user [-h] {alumni,create,convert,delete,offboard,reset,restore,signout} ...

positional arguments:
  {alumni,create,convert,delete,offboard,reset,restore,signout}
                        The user command to run.
    alumni              Convert a user account to a Compiler alumni.
    create              Create a new user in the Compiler domain.
    convert             Convert a user account to a new type.
    delete              Delete a user account.
    offboard            Offboard a user account.
    reset               Reset a user's password to a randomly generated string.
    restore             Restore an email backup from a prior offboarding.
    signout             Signs a user out from all active sessions.

options:
  -h, --help            show this help message and exit
```

### Creating a user

```bash
$ compiler-admin user create -h
usage: compiler-admin user create [-h] [--notify NOTIFY] username

positional arguments:
  username         A Compiler user account name, sans domain.

options:
  -h, --help       show this help message and exit
  --notify NOTIFY  An email address to send the newly created account info.
```

Additional options are passed through to GAM, see more about [GAM user create](https://github.com/taers232c/GAMADV-XTD3/wiki/Users#create-a-user)

### Convert a user

```bash
$ compiler-admin user convert -h
usage: compiler-admin user convert [-h] [--force] [--notify NOTIFY] username {alumni,contractor,partner,staff}

positional arguments:
  username              A Compiler user account name, sans domain.
  {alumni,contractor,partner,staff}
                        Target account type for this conversion.

options:
  -h, --help            show this help message and exit
  --force               Don't ask for confirmation before conversion.
  --notify NOTIFY       An email address to send the alumni's new password.
```

### Offboarding a user

```bash
$ compiler-admin user offboard -h
usage: compiler-admin user offboard [-h] [--alias ALIAS] [--force] username

positional arguments:
  username       A Compiler user account name, sans domain.

options:
  -h, --help     show this help message and exit
  --alias ALIAS  Account to assign username as an alias.
  --force        Don't ask for confirmation before offboarding.
```

This script creates a local backup of `USER`'s inbox, see [Restore](#restore-an-email-backup)

### Restore an email backup

Retore a backup from a prior [Offboarding](#offboarding-a-user) into the `archive@compiler.la` account.

```bash
$ compiler-admin user restore -h
usage: compiler-admin user restore [-h] username

positional arguments:
  username    The user's account name, sans domain.

options:
  -h, --help  show this help message and exit
```
