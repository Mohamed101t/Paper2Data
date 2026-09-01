# Security Policy

## Supported versions

Paper2Data is currently in the `1.0.x` release-candidate line. Security fixes are applied to the active development branch and the latest supported release line.

## Reporting a vulnerability

Please **do not open a public GitHub issue** for a suspected vulnerability that could expose user data or enable code execution.

Preferred process:

1. Open the repository's **Security** tab.
2. Choose **Report a vulnerability** / create a private security advisory.
3. Include the affected version, reproduction steps, expected impact, and any proof-of-concept material needed to understand the issue.

Please avoid including real private datasets in a report. Use synthetic records whenever possible.

## Security principles

Paper2Data's current MVP is offline-first. Important security controls include:

- parameterized database operations;
- SQLite foreign-key integrity checks;
- spreadsheet formula-injection protection for exported text;
- no intentional use of raw `eval` / `exec` for user input;
- user database files excluded from release packages and Git history;
- mutable application data stored outside the frozen executable directory.

## Windows binaries

Unsigned local builds may be blocked by Windows Smart App Control or enterprise application-control policies. Do not disable organization-managed security controls to distribute Paper2Data. Public binary releases should follow an appropriate publisher code-signing process.
