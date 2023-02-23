# Google Admin

Scripts used for various administrative tasks in Compiler's Google Workspace.

Built on top of [GAMADV-XTD3](https://github.com/taers232c/GAMADV-XTD3) and [GYB](https://github.com/GAM-team/got-your-back).

## Initial setup

These scripts require an initial setup of a GAMADV-XTD3 project, providing the necessary API access to the Google Workspace.

Follow the steps in the [GAMADV-XTD3 Wiki](https://github.com/taers232c/GAMADV-XTD3/wiki/#requirements), and read
[Compiler's setup notes](https://docs.google.com/document/d/1UEwQzJZyJEkRs3PRwOi0-KXwBFne70am4Nk9-_qYItE/edit#heading=h.gbmx14gcpp2a)
for more information.

Additionally, GYB is used for Gmail backup/restore. See the [GYB Wiki](https://github.com/GAM-team/got-your-back/wiki)
for more information.

**Note:** This setup can only be performed by administrators of the Compiler Google Workspace.

## Offboarding a user

**Usage:**

```bash
bin/offboard.sh USER [ALIAS]
```

* `USER` is the username (sans domain) to offboard
* `ALIAS` is optional, and is a username (sans domain) that will get an alias
   added for the offboarded `USER`

Read more about the [offboarding process in Compiler's notes](https://docs.google.com/document/d/1UEwQzJZyJEkRs3PRwOi0-KXwBFne70am4Nk9-_qYItE/edit#heading=h.liqi1hwxykhs).
