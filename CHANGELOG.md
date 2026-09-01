# Changelog

All notable changes to Paper2Data are documented here.

The project follows semantic versioning for public releases.

## [1.0.0-rc.1] - 2026-09-01

### Added

- Windows desktop MVP using PySide6 and SQLite.
- Offline project, field, and record management.
- Central field-type system with 41 stable internal field IDs.
- Arabic, English, French, Russian, and Chinese interface support.
- RTL/LTR-aware data-entry behavior.
- Light and dark application themes.
- Smart field-type suggestions based on field names.
- Typed Excel export and canonical CSV export.
- Unit, integration, security, E2E, GUI E2E, and performance test profiles.
- PyInstaller Windows release tooling and runtime-path handling.

### Security

- Added spreadsheet formula-injection protection.
- Added SQL-injection regression tests.
- Added database foreign-key integrity tests.
- Added unsafe dynamic-execution regression checks.
- Prevented local databases from entering release packages.

### Fixed

- Language switching and translation persistence behavior.
- Stable field values independent of translated labels.
- Records-view signal ordering that could miss the first loaded result set.
- Locale-aware number parsing for decimal and currency formats.
- Conda runtime DLL discovery during Windows packaging.

### Validation

- Latest local release quality gate: **124 tests passed** on Windows before packaging.

### Release note

The source is at release-candidate stage. Public Windows binary distribution should wait for final publisher-signing and distribution-channel validation.
