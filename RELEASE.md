# Release Process

This document outlines the standard operating procedure for cutting a new release of Laminar.

## 1. Pre-Release Checks
Before initiating a release, ensure:
- The `main` branch is passing all CI checks (GitHub Actions).
- You have pulled the latest changes locally.
- All intended features and bug fixes for this release have been merged.
- You have run local tests: `make test` and `make lint-backend`.

## 2. Update Versions
Laminar requires versions to be synchronized across the backend and frontend.

1. **Backend:** Update the version string in `src/inference_control_plane/__init__.py`.
   ```python
   __version__ = "1.1.0"
   ```
2. **Frontend:** Update the version in `frontend/package.json`.
   ```json
   "version": "1.1.0"
   ```
3. **Website:** Update any necessary version references in the website marketing copy (if applicable).

## 3. Update the Changelog
Open `CHANGELOG.md` and:
1. Change the `[Unreleased]` heading to `[1.1.0] - YYYY-MM-DD`.
2. Ensure all notable changes (Added, Changed, Deprecated, Removed, Fixed, Security) are documented accurately.
3. Add a new empty `[Unreleased]` section at the top.

## 4. Commit and Tag
Commit the version bump and changelog updates.

```bash
git add src/inference_control_plane/__init__.py frontend/package.json CHANGELOG.md
git commit -m "chore: bump version to v1.1.0"
git push origin main
```

Create a Git tag for the release. The tag **must** start with `v`.

```bash
git tag v1.1.0
git push origin v1.1.0
```

## 5. Publish the GitHub Release
1. Go to the GitHub repository -> Releases -> Draft a new release.
2. Select the `v1.1.0` tag you just pushed.
3. Title the release `v1.1.0`.
4. Copy the relevant section from `CHANGELOG.md` into the release description.
5. Click **Publish Release**.

## 6. Verify Automated CI/CD
Upon publishing the release, GitHub Actions will automatically trigger the deployment pipelines:
1. **Docker Images:** The API and Dashboard images will be built and pushed to GHCR with the `1.1.0` and `latest` tags.
2. **Python Package:** (Optional) The backend package will be uploaded to PyPI.
3. **NPM Package:** (Optional) The frontend package will be uploaded to GitHub Packages.

Verify that these automated actions complete successfully in the Actions tab.
