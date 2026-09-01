# Publishing Paper2Data to GitHub

## Recommended repository settings

**Repository name:** `Paper2Data`

**Description:**

> Offline-first Windows desktop app for turning paper forms into structured Excel/CSV data without spreadsheet expertise.

**Suggested topics:**

```text
python
pyside6
sqlite
data-entry
forms
offline-first
excel
csv
desktop-app
data-digitization
arabic
rtl
```

For a portfolio/public project, create the repository as **Public**. Do not initialize it with another README, `.gitignore`, or license because V7 already supplies those files.

## Prepare locally

From the Paper2Data project folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\prepare_github_repo.ps1
```

Then review:

```powershell
git status
```

Pay special attention to files under `presentation/resources/` and source translation `.ts` files: these should be tracked. Databases, exports, `.qm`, `build/`, `dist/`, and `release_output/` must not be tracked.

## First commit

```powershell
git add .
git status
git commit -m "feat: prepare Paper2Data v1.0 release candidate"
git branch -M main
```

## Connect your GitHub repository

After creating an empty GitHub repository, copy its HTTPS URL and run:

```powershell
git remote add origin https://github.com/<YOUR_USERNAME>/Paper2Data.git
git push -u origin main
```

If `origin` already exists:

```powershell
git remote -v
```

Do not overwrite an existing remote until you have confirmed it points to the correct repository.

## Release-candidate tag

Because public Windows binary signing is still a separate release concern, use an RC tag first:

```powershell
git tag -a v1.0.0-rc.1 -m "Paper2Data v1.0.0 release candidate 1"
git push origin v1.0.0-rc.1
```

Reserve `v1.0.0` for the final approved release.

## GitHub repository options

After the first push:

1. Enable **Issues** if you want public bug/feature reports.
2. Keep **Security Advisories** available for private vulnerability reports.
3. Add the suggested repository topics.
4. Confirm the Actions workflow is green.
5. Do not upload the `*-UNVERIFIED.zip` package as a final release asset.

## Branch protection (recommended after CI is visible)

Protect `main` and require the CI workflow before merging pull requests. For a solo portfolio repository you can still allow direct pushes during early development, then tighten protection as contributors arrive.
