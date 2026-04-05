# Sextant — Cursor Plugin

Architecture-aware engineering principles for Cursor IDE.

## Requirements

- Python 3.7+
- Cursor IDE

## Install

Clone the repository and run the installer from your project directory:

```bash
git clone https://github.com/hellotern/sextant
cd your-project
python path/to/sextant/.cursor-plugin/install.py
```

This writes rules and commands directly into `.cursor/` in your current directory.

### Global install (all Cursor projects)

```bash
python path/to/sextant/.cursor-plugin/install.py --global
```

Installs into `~/.cursor/`, making Sextant available in every Cursor project.

### Uninstall

```bash
# Project-level
python path/to/sextant/.cursor-plugin/install.py --uninstall

# Global
python path/to/sextant/.cursor-plugin/install.py --global --uninstall
```

## What Gets Installed

| File | Type | Behavior |
|------|------|----------|
| `.cursor/rules/sextant-principles.mdc` | Rule | Always active — injects §0–§6 engineering principles into every AI interaction |
| `.cursor/rules/sextant-gitnexus.mdc` | Rule | Active when `.gitnexus/` exists — injects GitNexus MCP tool guidance |
| `.cursor/commands/sextant-fix-bug.md` | Command | `/sextant-fix-bug` |
| `.cursor/commands/sextant-add-feature.md` | Command | `/sextant-add-feature` |
| `.cursor/commands/sextant-modify-feature.md` | Command | `/sextant-modify-feature` |
| `.cursor/commands/sextant-debug.md` | Command | `/sextant-debug` |
| `.cursor/commands/sextant-plan.md` | Command | `/sextant-plan` |
| `.cursor/commands/sextant-ship.md` | Command | `/sextant-ship` |
| `.cursor/commands/sextant-migrate.md` | Command | `/sextant-migrate` |
| `.cursor/commands/sextant-review-code.md` | Command | `/sextant-review-code` |
| `.cursor/commands/sextant-write-tests.md` | Command | `/sextant-write-tests` |
| `.cursor/commands/sextant-refine-requirements.md` | Command | `/sextant-refine-requirements` |
| `.cursor/commands/sextant-security.md` | Command | `/sextant-security` |
| `.cursor/commands/sextant.md` | Command | `/sextant` (fallback) |

## Usage

- **Principles are automatic** — no action needed, they apply to all Cursor AI interactions.
- **Invoke a workflow** — type `/` in Cursor chat, then select a sextant command:
  - `/sextant-fix-bug` — restoring broken behavior
  - `/sextant-add-feature` — building new functionality
  - `/sextant-modify-feature` — changing or refactoring existing code
  - `/sextant-debug` — locating an unknown bug
  - `/sextant-review-code` — evaluating code quality
  - `/sextant-write-tests` — adding test coverage
  - `/sextant-refine-requirements` — scoping ambiguous work
  - `/sextant-plan` — sequencing a multi-step implementation
  - `/sextant-ship` — preparing a PR or release
  - `/sextant-migrate` — coordinating a cross-module upgrade
  - `/sextant-security` — auditing for vulnerabilities
  - `/sextant` — lightweight fallback for quick tasks

## Updating

Pull the latest version of the repo and re-run the installer:

```bash
cd sextant && git pull
cd your-project && python path/to/sextant/.cursor-plugin/install.py
```

## How It Works

The installer reads skill definitions from `skills/` in the repo root, resolves
`!` file-include directives (a Claude Code convention) by inlining the referenced
content, and writes the result as Cursor-compatible `.mdc` rule files and `.md`
command files. No intermediate files are stored in the repo.
