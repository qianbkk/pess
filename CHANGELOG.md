# PESS v3.2.0 (TBD)

## What's New in v3.2.0

### CI/CD Integration
- Added GitHub Actions workflow template: `templates/ci/github-actions/pess-quality.yml`
  - Validates Memory Bank structure
  - Checks CLAUDE.md presence
  - Scans for hardcoded secrets and absolute paths
  - Runs project tests if available

### /doctor Command
- Added `templates/commands/doctor.md` — PESS system health check
  - Hooks installation status
  - Project initialization validation
  - Memory Bank health (freshness, size, lessons count)
  - Guard hooks functional test

### pess-update
- Added `pess-update.ps1` (Windows) and `pess-update.sh` (macOS/Linux)
  - Check for updates: `--check` / `-CheckOnly`
  - Preserves user customizations (CLAUDE.md, memory-bank)
  - Shows changelog summary between versions

---

## Migration from v3.1

Run `pess-update.ps1` or `bash pess-update.sh` to fetch latest changes without overwriting your customizations.

To use CI/CD quality gates, copy the template:
```bash
cp templates/ci/github-actions/pess-quality.yml .github/workflows/
```