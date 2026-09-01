# Windows Release Checklist

Use this checklist before publishing a public Paper2Data binary.

## 1. Source quality

- [ ] Working tree contains only intended changes.
- [ ] `python scripts/repository_health_check.py` passes.
- [ ] Translation catalogs are complete.
- [ ] `python scripts/run_tests.py full` passes.

## 2. Build

- [ ] Build translations.
- [ ] Install pinned/approved release dependencies.
- [ ] Build `dist/Paper2Data/` using the release script.
- [ ] Confirm required Conda/Python runtime DLLs are bundled.
- [ ] Confirm no `.db`, `-wal`, or `-shm` files exist in the release directory.

## 3. Smoke test

- [ ] Launch the packaged executable on a suitable Windows test environment.
- [ ] Create a project.
- [ ] Add representative field types.
- [ ] Enter and save multiple records.
- [ ] Close and reopen the application; confirm data persists.
- [ ] Switch all five UI languages.
- [ ] Verify Arabic RTL and LTR data-field behavior.
- [ ] Test light and dark themes.
- [ ] Export `.xlsx` and `.csv` and inspect results.

## 4. Security / signing

- [ ] Do not disable organization-managed application-control policies for release validation.
- [ ] Sign public Windows binaries with the chosen publisher code-signing process.
- [ ] Verify the Authenticode signature.
- [ ] Re-run smoke tests on the signed artifact.

## 5. Publication

- [ ] Generate SHA-256 checksum.
- [ ] Ensure the archive is not named `UNVERIFIED`.
- [ ] Create a Git tag.
- [ ] Write release notes.
- [ ] Upload only approved artifacts.
- [ ] Verify the downloaded GitHub artifact on a clean/test machine.

## Release rule

**A successful PyInstaller build is not the same as a successful product release.** The packaged executable must also pass its smoke test and distribution trust requirements.
