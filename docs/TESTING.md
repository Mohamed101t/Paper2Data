# Testing Strategy

Paper2Data treats tests as release gates, not optional examples.

## Profiles

| Profile | Purpose | Command |
| --- | --- | --- |
| Quick | Day-to-day regression suite | `python scripts/run_tests.py quick` |
| Unit | Isolated domain/service/component behavior | `python scripts/run_tests.py unit` |
| Integration | SQLite, repositories, exporters, viewmodels together | `python scripts/run_tests.py integration` |
| Security | Security and data-integrity regressions | `python scripts/run_tests.py security` |
| E2E | Headless user workflow | `python scripts/run_tests.py e2e` |
| GUI | Offscreen PySide6 end-to-end smoke flow | `python scripts/run_tests.py gui` |
| Performance | Scale/timing regression budgets | `python scripts/run_tests.py performance` |
| Full | Release-candidate suite | `python scripts/run_tests.py full` |

## What is tested

### Unit

- field-type normalization and aliases;
- type metadata;
- validation rules;
- localized/locale-aware numeric parsing;
- export mapping;
- spreadsheet-safety helpers;
- runtime data/resource paths;
- translation catalog completeness.

### Integration

- real temporary SQLite databases;
- repositories and relational integrity;
- typed storage and export;
- viewmodel signal ordering.

### Security

- SQL-injection attempts treated as data;
- spreadsheet formula-injection handling;
- SQLite foreign-key behavior;
- accidental sensitive console output;
- raw unsafe dynamic execution checks.

### E2E

The workflow exercises project creation, fields, record entry, persistence, record loading, export, and deletion. A GUI-specific smoke test exercises the PySide6 presentation flow in offscreen mode.

### Performance

Performance tests intentionally run separately from everyday quick tests. The current MVP includes regression budgets for large record retrieval and Excel/CSV export workloads.

## Latest local release gate

On 2026-09-01, the Windows release-candidate quality gate completed with:

```text
124 passed
```

Hosted CI results may differ in timing; performance thresholds should be reviewed carefully before enforcing them on shared runners.
