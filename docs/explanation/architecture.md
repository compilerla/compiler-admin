# Architecture Overview

This document provides a high-level overview of the `compiler-admin` codebase structure, intended for developers who may want to contribute to the project.

The project is organized into three main layers:

```
compiler_admin/
├── api/
├── commands/
└── services/
```

## `commands/`

This directory contains the definition of the command-line interface. The project uses the [Click](https://click.palletsprojects.com/) library to build the CLI.

-   Each subcommand (e.g., `info`, `init`, `time`, `user`) has its own module.
-   For nested commands like `time` and `user`, the `__init__.py` file in the respective directory acts as a command group that aggregates the subcommands from the other modules in that directory.
-   These modules are responsible for parsing CLI arguments and options. They should contain minimal business logic, instead calling functions in the `services/` layer to perform the actual work.

## `services/`

This directory contains the core business logic of the application.

-   Each module in this directory is responsible for a specific domain of functionality (e.g., `google.py` for Google Workspace interactions, `toggl.py` for Toggl-related logic, `harvest.py` for Harvest-related logic).
-   These services are where the interactions with external tools (like `gam` and `gyb`) and APIs happen.
-   Functions in this layer are called by the `commands/` layer and are designed to be reusable.

## `api/`

This directory contains low-level clients for interacting with third-party HTTP APIs.

-   For example, `api/toggl.py` contains a `Toggl` class that is a direct client for the Toggl Track REST API.
-   This layer is responsible for handling the details of HTTP requests, authentication, and response handling.
-   The `services/` layer uses these API clients to implement its logic. For instance, `services/toggl.py` might use the `api.toggl.Toggl` client to download a report, and then perform data processing on the result.

This separation of concerns makes the application easier to understand, maintain, and test.
