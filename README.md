# Compiler Admin

Automating Compiler's administrative tasks.

Built on top of [GAM7](https://github.com/GAM-team/GAM) and [GYB](https://github.com/GAM-team/got-your-back).

**Note:** This tool can only be used by those with administrator access to Compiler's Google Workspace.

## Basic Usage

```console
$ compiler-admin --help
Usage: compiler-admin [OPTIONS] COMMAND [ARGS]...

  Compiler's command line interface.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  info  Print information about the configured environment.
  init  Initialize a new GAM and/or GYB project.
  ls    Print information about the Compiler org.
  time  Work with Compiler time entries.
  user  Work with users in the Compiler org.
```
