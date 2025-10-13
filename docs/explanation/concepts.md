# Core Concepts

This section explains some of the foundational concepts and external tools that `compiler-admin` is built upon.

## External Tools: GAM and GYB

The `compiler-admin` tool is fundamentally a wrapper that simplifies and automates common administrative workflows by building on two powerful, open-source command-line tools for Google Workspace administration:

-   **[GAM (Google Apps Manager)](https://github.com/GAM-team/GAM):** GAM7 provides comprehensive control over nearly every aspect of a Google Workspace account, from managing users, groups, and OUs to controlling service settings and Drive permissions. `compiler-admin` uses GAM7 for all user and group management tasks like creating users, changing their OU, and resetting passwords.

-   **[GYB (Got Your Back)](https://github.com/GAM-team/got-your-back):** GYB is a specialized tool for backing up and restoring Gmail mailboxes. `compiler-admin` uses GYB during the user offboarding process to create a complete, local backup of a user's inbox before the account is deactivated or deleted.

By using these tools, `compiler-admin` avoids reinventing the wheel and can focus on providing a streamlined interface for Compiler's specific administrative workflows.

## User Account Types

Compiler organizes its Google Workspace users into several types, which correspond to a combination of Organizational Units (OUs) and Google Groups. This structure determines a user's access and permissions.

-   **Staff (`OU: staff`, `Group: staff@, team@`)**: Full-time employees.
-   **Partners (`OU: staff/partners`, `Group: partners@, staff@, team@`)**: Company partners, who are a subset of staff but with additional permissions.
-   **Contractors (`OU: contractors`, `Group: team@`)**: External contractors with more limited access than staff.
-   **Alumni (`OU: alumni`)**: Deactivated accounts of former employees. They have no group memberships and cannot log in.

The `user convert`, `user deactivate`, and `user reactivate` commands are the primary tools for moving users between these types.

## Time Reporting Workflow

The company uses multiple systems for time tracking and invoicing, which necessitates converting time reports between different formats.

1.  **Toggl Track**: This is the primary system where all team members track their time.
2.  **Harvest / Justworks**: These are secondary systems used for invoicing, payroll, or project management.

The `time` commands in `compiler-admin` facilitate this workflow:
-   `time download`: Exports detailed time entries from Toggl.
-   `time convert`: Converts the Toggl CSV format into a format compatible with Harvest or Justworks.
-   `time verify`: Provides a way to check that the data remains consistent after conversion.
-   `time lock`: Locks the entries in Toggl after the data has been exported and processed, ensuring the integrity of the invoiced records.
