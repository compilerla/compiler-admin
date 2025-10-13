# Configuration

The `compiler-admin` tool can be configured using the following environment variables.

## Toggl Configuration

| Variable             | Description                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------ |
| `TOGGL_API_TOKEN`    | **Required.** Your API token for the Toggl Track API.                                                        |
| `TOGGL_WORKSPACE_ID` | **Required.** The ID of your Toggl workspace.                                                                |
| `TOGGL_CLIENT_NAME`  | The name of the client to use when converting reports from Harvest to Toggl format.                          |
| `TOGGL_PROJECT_INFO` | Path to a JSON file used to cache Toggl project information. This helps map Toggl projects to other systems. |
| `TOGGL_USER_INFO`    | Path to a JSON file used to cache Toggl user information.                                                    |

## Harvest Configuration

| Variable              | Description                                                                         |
| --------------------- | ----------------------------------------------------------------------------------- |
| `HARVEST_CLIENT_NAME` | The name of the client to use when converting reports from Toggl to Harvest format. |

## Google Workspace (GAM/GYB) Configuration

| Variable    | Description                                                                           |
| ----------- | ------------------------------------------------------------------------------------- |
| `GAMCFGDIR` | The directory where GAM7 stores its configuration files. Defaults to `./.config/gam`. |

## Data Conversion

| Variable       | Description                                                                                            |
| -------------- | ------------------------------------------------------------------------------------------------------ |
| `TOGGL_DATA`   | The default input path for the `time convert` command when converting from Toggl. Defaults to stdin.   |
| `HARVEST_DATA` | The default output path for the `time convert` command when converting to Harvest. Defaults to stdout. |
