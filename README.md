# Sextant

**Sextant** is a [Claude Code](https://claude.ai/code) skill that provides systematic, tiered workflows for common coding tasks — bug fixes, new features, refactoring, code review, test writing, and requirements refinement.

Like a nautical sextant that helps navigators determine their exact position before charting a course, this skill helps AI coding agents understand where they are in the codebase before making changes.

---

## How It Works

Sextant operates as a **layered skill system**:

1. **Task Detection** — The skill identifies the type of task (bug fix, new feature, etc.) and loads the corresponding reference workflow
2. **Scale Assessment** — Rules are activated proportionally to task size (lightweight / medium / large)
3. **Workflow Execution** — The agent follows the structured workflow, applying only the principles relevant to the current task

### Task Types

| Task Type | Reference File |
|-----------|---------------|
| Bug Fix | `references/bugfix.md` |
| New Feature / Module | `references/new-module.md` |
| Modify / Enhance / Refactor | `references/modify-existing.md` |
| Code Review | `references/review.md` |
| Write Tests | `references/testing.md` |
| Requirements Analysis & Refinement | `references/refine-requirements.md` |

### Rule Scaling

Rules are activated based on task scale — not every task needs the full ruleset:

| Scale | Trigger | Active Rules |
|-------|---------|--------------|
| **Lightweight** | Single-function adjustments, config changes, style fixes | Baseline rules only (§4) |
| **Medium** | New functions/classes, module-internal changes, bug fixes | + SRP, DRY, interface contracts |
| **Large** | Cross-module changes, public interface modifications, new modules | Full SOLID + impact analysis + architecture audit |

### Exempt Scenarios

The following are exempt from most rules (baseline rules still apply):
- One-off scripts / temporary tools
- Demos / prototypes / POCs
- Algorithm problems / competitive programming
- Notebooks / data exploration

---

## Core Principles

### SOLID
- **SRP** — Every module, class, and function has one responsibility and one reason to change
- **OCP** — Open for extension, closed for modification; new behavior via extension, not modification
- **LSP** — Subclasses must be transparently substitutable for their base classes
- **ISP** — Interfaces stay small; implementors are not forced to depend on unused methods
- **DIP** — High-level modules depend on abstractions, not concrete implementations

### Architecture Constraints
- **Hollywood Principle** — Modules declare dependencies (injected); they don't proactively pull them
- **Dependency Direction** — Entry → Logic → Data → Infrastructure (one-way, no reversal)
- **Module Boundaries** — Cross-module communication via public interfaces or event bus only

### Code Quality Baselines (Always Active)
- Never swallow exceptions
- No magic numbers or strings
- Accurate function naming
- Validate all parameters at public interfaces
- Explicit type declarations
- Meaningful log messages
- Explicit dependency declaration
- Side effects isolated from pure computation

---

## Optional: GitNexus Integration

Sextant has first-class support for [GitNexus](https://gitnexus.dev), an MCP-based code knowledge graph tool. When GitNexus is available, it replaces slow manual grep/read workflows with precise graph queries:

| Manual Approach | GitNexus Approach |
|----------------|-------------------|
| Grep for function name, read call chain file by file | `context` returns complete caller/callee graph in one call |
| Estimate "what will this change break" | `impact` returns layered impact list with confidence scores |
| Use `pydeps` / `madge` for circular dependency detection | `impact both` queries the graph directly, covering all languages |
| Search for similar implementations to avoid duplication | `query` semantic search + cluster membership |
| Manually assess `git diff` impact | `diff_review` analyzes change impact automatically |

To enable GitNexus, run `npx gitnexus analyze` in your project root. The skill detects the resulting `.gitnexus/` directory automatically and activates enhanced mode.

---

## Installation

### As a User Skill (applies to all projects)

```bash
git clone https://github.com/your-username/sextant ~/.claude/skills/sextant
```

### As a Project Skill (applies to current project only)

```bash
git clone https://github.com/your-username/sextant .claude/skills/sextant
```

---

## File Structure

```
coding-principles/
├── SKILL.md                        # Main skill: task detection, SOLID, DRY, baselines
└── references/
    ├── bugfix.md                   # Bug fix workflow
    ├── new-module.md               # New feature / module workflow
    ├── modify-existing.md          # Modify / refactor existing code workflow
    ├── review.md                   # Code review workflow
    ├── testing.md                  # Test writing workflow
    ├── refine-requirements.md      # Requirements analysis and refinement workflow
    └── gitnexus-integration.md     # GitNexus MCP tool reference (optional)
```

---

## Design Philosophy

**Principles are tools, not chains.** The goal is the lowest long-term maintenance cost for the team. When principles conflict, that standard is the final arbiter.

**Only activate what the task needs.** A one-line bug fix doesn't need a full architecture audit. The skill scales its rigor to match the scope of the work.

**Understand before acting.** Every workflow starts with reading and understanding the existing code and its context before writing a single line. Changing code without reading it is like rerouting plumbing without a floor plan.

---

## License

MIT
