# How to Run the Monthly Time Reporting GitHub Actions Workflow

This guide explains how to manually trigger and monitor the `Monthly Time Reporting` GitHub Actions workflow, which automates the process of downloading, converting, verifying, and posting monthly time reports.

## Overview

The workflow performs the following automated steps:

- **Lock Toggl time entries**: Locks time entries in Toggl up to the specified `end-date` (or end of prior month).
- **Download Toggl time entries**: Downloads a detailed CSV report from Toggl.
- **Convert Toggl entries to Harvest format**: Converts the downloaded report into a Harvest-compatible CSV.
- **Verify time entries**: Compares the downloaded and converted files to ensure data integrity, and generates a summary.
- **Post to Slack**: Sends the summary and the converted Harvest CSV to a designated Slack channel.

This workflow ensures that monthly time reporting is consistent and automated.

## Prerequisites

To run this workflow, you must have:

- Write access to the GitHub repository.
- The necessary GitHub Secrets configured in the repository settings. These secrets include API tokens and configuration for Toggl, Harvest, Google Workspace (GAM), and Slack. Without these, the workflow will fail.

## Locating the Workflow

The workflow definition file is located at:
[`./.github/workflows/time-reporting.yml`](https://github.com/compilerla/compiler-admin/blob/main/.github/workflows/time-reporting.yml)

## Manually Triggering the Workflow

To manually trigger the workflow:

1. Navigate to the [**Actions**](https://github.com/compilerla/compiler-admin/actions) tab in the GitHub repository.
2. In the left sidebar, click on the **Monthly Time Reporting** workflow.
3. On the workflow page, click the **Run workflow** dropdown button.
4. Leave the `Branch: main` selection as-is.
5. You will see optional input fields for `start-date` and `end-date`.
   - If left blank, the workflow will default to the previous calendar month.
   - Enter dates in `YYYY-MM-DD` format if you need to process a specific period.
6. Click the green **Run workflow** button to start the execution.

## Monitoring a Workflow Run

After triggering, you will be redirected to the workflow run page (you may need to refresh).

1. Click on the active workflow run to view its progress.
2. You can expand each job step (e.g., "Lock Toggl time entries", "Download Toggl time entries", "Verify time entries") to see its detailed output.
3. The final step, "Post to Slack", will send a summary of the time report to the configured Slack channel and upload the converted Harvest CSV file.
