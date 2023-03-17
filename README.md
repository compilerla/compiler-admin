# Google Admin

Administrative tasks in Compiler's Google Workspace.

Built on top of [GAMADV-XTD3](https://github.com/taers232c/GAMADV-XTD3) and [GYB](https://github.com/GAM-team/got-your-back).

## Initial setup

Initial setup of a GAMADV-XTD3 project is required to provide necessary API access to the Google Workspace.

Follow the steps in the [GAMADV-XTD3 Wiki](https://github.com/taers232c/GAMADV-XTD3/wiki/#requirements), and read
[Compiler's setup notes](https://docs.google.com/document/d/1UEwQzJZyJEkRs3PRwOi0-KXwBFne70am4Nk9-_qYItE/edit#heading=h.gbmx14gcpp2a)
for more information.

Additionally, GYB is used for Gmail backup/restore. See the [GYB Wiki](https://github.com/GAM-team/got-your-back/wiki)
for more information.

**Note:** This setup can only be performed by those with administrator access to Compiler's Google Workspace.

## Creating a user

**Usage:**

```bash
bin/create.sh USER [OPTIONS]
```

- `USER` is the username (sans domain) to create
- `OPTIONS` is a list of options for [GAM user create](https://github.com/taers232c/GAMADV-XTD3/wiki/Users#create-a-user)

## Convert a user

**Usage:**

```bash
bin/convert.sh USER TYPE
```

- `USER` is the username (sans domain) to convert
- `TYPE` is either `STAFF` to convert the user to a staff member, or `PARTNER` to conver the user to a partner.

## Offboarding a user

**Usage:**

```bash
bin/offboard.sh USER [ALIAS]
```

- `USER` is the username (sans domain) to offboard
- `ALIAS` is optional, and is a username (sans domain) that will get an alias
  added for the offboarded `USER`

Read more about the [offboarding process in Compiler's notes](https://docs.google.com/document/d/1UEwQzJZyJEkRs3PRwOi0-KXwBFne70am4Nk9-_qYItE/edit#heading=h.liqi1hwxykhs).

This script creates a local backup of `USER`'s inbox; a separate script can be run to archive this backup into the `archive@compiler.la` account:

```bash
bin/archive-gmail-backup.sh USER
```

- `USER` is the account in compiler.la (sans domain) with a local backup to archive
