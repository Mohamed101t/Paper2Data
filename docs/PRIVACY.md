# Privacy and Local Data

Paper2Data's current MVP is designed as an **offline-first** desktop application.

## Local storage

Records are stored in SQLite. A packaged Windows build places writable application data in the user's local application-data area rather than inside the application bundle.

## Network behavior

The current MVP does not require a Paper2Data cloud account, cloud synchronization, telemetry service, or online API to perform its primary data-entry workflow.

URL fields are validated as data; their presence does not imply that Paper2Data sends those values over the network.

## Exports

Users explicitly choose when and where to create Excel or CSV files. Those exported files may contain sensitive information depending on the user's project, so users are responsible for storing and sharing them appropriately.

## Repository hygiene

The Git repository excludes local SQLite databases, user exports, release output, credentials, and generated binary artifacts. Contributors must use synthetic data in tests and examples.

## Future features

If cloud sync, telemetry, OCR services, or AI-assisted extraction are introduced in a future release, their data flows and consent/privacy implications must be documented before release.
