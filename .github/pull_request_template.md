## Summary

<!-- What user/developer problem does this change solve? -->

## Scope

<!-- Keep the PR focused on one responsibility. -->

## Testing

- [ ] `python scripts/run_tests.py quick`
- [ ] `python scripts/run_tests.py security` (if relevant)
- [ ] `python scripts/run_tests.py gui` (if UI behavior changed)
- [ ] `python scripts/run_tests.py performance` (if scale/export/database behavior changed)

## Localization / RTL

- [ ] Visible strings updated in translation catalogs when needed
- [ ] Arabic RTL behavior checked when relevant
- [ ] Stable internal field IDs were not changed merely to rename labels

## Repository hygiene

- [ ] No databases, exports, credentials, build output, personal paths, or private datasets were added
- [ ] `python scripts/repository_health_check.py` passes
