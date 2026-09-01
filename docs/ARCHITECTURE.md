# Architecture

Paper2Data uses a layered desktop architecture designed to keep business rules testable and UI code replaceable.

## Layers

### `domain/`

Contains the application's business vocabulary and rules:

- entities such as Project, Field, Record;
- repository abstractions;
- field-type definitions;
- value validation and normalization;
- field-type suggestion logic.

The domain layer should not depend on PySide6 widgets or SQLite implementation details.

### `data/`

Contains concrete repository implementations. It translates domain operations into persistence operations while keeping storage decisions outside the presentation layer.

### `core/`

Contains cross-cutting infrastructure:

- SQLite database service;
- export mapping and Excel/CSV services;
- localization service;
- runtime/resource path resolution;
- spreadsheet-safety helpers;
- shared error types.

### `presentation/`

Contains PySide6-specific UI:

- views;
- viewmodels;
- reusable components;
- theme/design system;
- translation catalogs.

Views should focus on rendering and interaction. Validation, storage, and export rules belong outside views whenever practical.

## Dependency direction

```text
presentation
     ↓
domain abstractions
     ↑
data implementations

core services support the application at explicit boundaries.
```

## Stable field identifiers

Translated labels are presentation concerns. Persisted field types use stable IDs such as `short_text`, `integer`, `date`, and `phone_number` so a language switch cannot corrupt business logic or exports.

## Runtime data

Source runs preserve the development workflow. Frozen Windows builds resolve mutable data to a writable per-user location rather than placing the SQLite database beside the executable.

## Design system

The presentation layer centralizes visual behavior in theme/components rather than repeating raw Qt styling throughout screens. This supports consistency across light/dark modes and future desktop UI evolution.
