---
description: >-
  Use when migrating code from one version, technology, or pattern to another — such as Vue 2 → Vue 3, JavaScript → TypeScript, database schema migration, or framework upgrades. Stronger signals: "migrate", "upgrade", "convert", "port", "move from X to Y". Distinct from sextant:modify-feature (single module behavior change); use this when multiple modules must change in a coordinated sequence with rollback points.
---

!`python3 ${CLAUDE_SKILL_DIR}/../principles/strip_frontmatter.py ${CLAUDE_SKILL_DIR}/../principles/SKILL.md`

!`python3 ${CLAUDE_SKILL_DIR}/../principles/strip_frontmatter.py ${CLAUDE_SKILL_DIR}/../tool-gitnexus/SKILL.md --if-dir-exists .gitnexus`

---

# Migration Workflow

## Core Principle

Migrations are multi-module, stateful, and partially irreversible. The core strategy is **migrate in dependency order, validate at every checkpoint, and keep rollback options open until all modules are confirmed working.**

> **Distinct from sextant:modify-feature:** Modify-feature changes one module's behavior. Migration coordinates changes across many modules in a defined sequence, with compatibility shims and a rollback plan at each phase boundary.

---

## Complete Execution Workflow

### Step 1: Migration Scope Scan

Enumerate all affected files and produce a migration inventory:

- List every file that references the old API, type, pattern, or version
- Score the total impact using the Impact Radius Scorecard (§3.2)
- Identify dependency relationships between affected files

```
Migration Inventory
─────────────────────────────────────────────
Migration: <from X> → <to Y>
Impact radius score: N → <Tier>

File                   | Change Type             | Dependency Order
───────────────────────|─────────────────────────|──────────────────────
<file A>               | <API call → new API>    | leaf (migrate first)
<file B>               | <type annotation>       | depends on A
<file C>               | <core module>           | migrate last
─────────────────────────────────────────────
```

🔗 When GitNexus is available, use `impact` MCP tool to enumerate all dependents automatically.

### Step 2: Compatibility Assessment

For each breaking change in the migration:

- Is there a **compatibility shim** available (e.g., an adapter, polyfill, or compatibility layer)?
- What is the **backward compatibility window** — can the old and new API coexist during migration?
- Is there **runtime coercion risk** — can old data be silently misinterpreted by the new code?

```
Compatibility Assessment
─────────────────────────────────────────────
Breaking change: <description>
  Shim available:         Yes (<name / approach>) / No
  Old/new coexistence:    Yes (window: <duration / version range>) / No
  Runtime coercion risk:  Yes (describe) / No
  Rollback approach:      <how to revert this step if it fails>
─────────────────────────────────────────────
```

**If no shim is available and old/new cannot coexist:** flag as a hard-cutover migration step. These steps require explicit user authorization before execution.

### Step 3: Migration Order Planning

**Ordering rule (per §6.2 dependency direction):** migrate leaf modules first, core modules last.

```
Migration Sequence
─────────────────────────────────────────────
Phase 1 (no dependents): <leaf files — safe to migrate first>
Phase 2 (depend on Phase 1 only): <next tier>
...
Phase N (core): <modules with the most dependents — migrate last>

Rollback boundary after each phase: if Phase N+1 fails, revert only Phase N.
─────────────────────────────────────────────
```

**Each phase should be a separate commit** — this preserves rollback granularity and makes the migration history bisectable.

### Step 4: Per-Module Migration + Validation

For each module, in the order established in Step 3:

1. Apply the migration to this module only
2. Run the associated tests for this module (and its direct callers)
3. **If tests pass:** continue to the next module
4. **If tests fail:** stop. Do not continue to the next module. Diagnose the failure — link `sextant:debug` if the root cause is not immediately clear.

```
Per-Module Migration Log
─────────────────────────────────────────────
Module: <file / module name>
Change applied: <description>
Tests run: <test file(s) or test command>
Result: ✅ Pass — proceed to next module / ❌ Fail — stopped (diagnosis below)
─────────────────────────────────────────────
```

**Forbidden:** Migrating multiple modules between test runs. Each module migration must be validated before the next begins.

### Step 5: Legacy Code Cleanup

After all modules pass validation, remove migration scaffolding in a **separate commit**:

- Delete compatibility shims and adapters
- Remove old type aliases and version-compatibility branches
- Remove `@deprecated` annotations added for this migration
- Remove feature flags introduced to gate the migration

```
Cleanup Checklist
─────────────────────────────────────────────────────
[ ] Compatibility shims removed
[ ] Old type aliases / version branches deleted
[ ] @deprecated annotations cleared
[ ] Migration feature flags removed
[ ] Tests updated to remove compatibility-mode paths
[ ] Documentation updated (README, CHANGELOG, migration guide)
─────────────────────────────────────────────────────
```

> **Why a separate commit?** Cleanup changes are low-risk and mechanical. Keeping them separate from functional migration changes makes both easier to review and easier to bisect if a regression appears later.

---

## Forbidden Actions

- Do not migrate multiple modules in a single step without validating each — this removes rollback granularity
- Do not delete the old API or shim before all consumers have been migrated and tested
- Do not make behavioral changes alongside migration changes — migration commits must be pure migrations (structure changes only, behavior preserved)

---

## Sprint State Integration

If `.sextant/state.json` exists in the project root and the current task matches a sprint task:

- **On start:** offer to update the task's `status` from `pending` → `in_progress`. Ask: *"Update sprint state to mark Task N as in_progress?"*
- **On completion** (acceptance condition met): offer to update `status` to `done`. Ask: *"Update sprint state to mark Task N as done?"*
- **On blocker** (test failure, missing dependency, unresolvable ambiguity that halts progress): surface the issue, then ask: *"Mark Task N as blocked and record the reason in flags?"* If confirmed, set `status: "blocked"` and append `{"task": N, "reason": "<one-sentence blocker description>"}` to the top-level `flags` array. Do not proceed to the next task while a task is blocked.

Do not write the file without explicit user confirmation. If the user declines, continue without state updates.

---

## Reply Format

```
─── Migration Summary ───────────────────────────────
① Scope:             <N files; impact radius N → Tier; N phases planned>
② Compatibility:     <shims available / hard-cutover steps flagged (N require authorization)>
③ Sequence:          <phase-by-phase plan with rollback boundaries>
④ Current status:    <Phase N of M: ✅ complete / ❌ stopped at <module> (diagnosis: <root cause>)>
⑤ Needs your input: <hard-cutover steps requiring explicit authorization; test failures to diagnose>
─────────────────────────────────────────────────────
```
