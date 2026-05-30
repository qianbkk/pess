# AGENTS.md

## Build
- Install: `.\pess-install.ps1` (run once)
- Use: `pess-init -ProjectName "my-project" -ProjectType "python-fastapi"`
- Test: `.\tests\test-init.ps1` (see tests/ directory)
- Lint: hooks scripts → `ruff check hooks/`

## Constraints
- Hook scripts must stay in `hooks/` (source); deployment is to user-level via pess-install.ps1
- Template files must have no hardcoded absolute paths (use placeholders like [PROJECT_NAME])
- Never auto-generate CLAUDE.md content with LLM (ETH Zurich arXiv:2602.11988)
- Skill description fields are triggers, not documentation

## Architecture
- Entry point: pess-init.ps1 (project scaffolding)
- Install script: pess-install.ps1 (one-time global setup)
- Templates: templates/ directory (read-only source of truth)
- Hooks: hooks/ directory (source); deployed to %USERPROFILE%\.claude\hooks\ by installer

## File Roles
- hooks/*.py           → user-level security guards (NOT repo-level)
- templates/global-CLAUDE.md → copied to ~/.claude/CLAUDE.md by installer
- templates/commands/  → copied into .claude/commands/ by pess-init
- templates/skills/    → copied into .claude/skills/ by pess-init
- templates/*/CLAUDE.md → project-type-specific templates