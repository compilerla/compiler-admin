# Compiler Admin

Automating Compiler's administrative tasks.

Built on top of [GAM7](https://github.com/GAM-team/GAM) and [GYB](https://github.com/GAM-team/got-your-back).

**Note:** This tool can only be used by those with administrator access to Compiler's Google Workspace.

## Basic Usage

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
