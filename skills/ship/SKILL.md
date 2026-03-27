---
description: >-
  You MUST use this skill before creating a PR, bumping a version, or declaring work ready to merge.
  Use when the implementation is done and the goal is to get it across the finish line — PR creation, changelog, version bump, final pre-merge checks.
  Stronger signals: "ship this", "create a PR", "write changelog", "bump version", "prepare for merge", "what do I need before merging", "ready to release".
  Use sextant:review-code instead when the goal is to evaluate code quality, not to prepare it for shipping.
---

!../principles/SKILL_BODY.md

!../tool-gitnexus/SKILL_BODY.md

---

# Ship / Release Preparation Workflow

## Core Principle

Code is not done when it compiles — it is done when it is safely merged, documented, and verifiable by the next person who touches it. This skill bridges the gap between "implementation complete" and "PR merged."

> **Scope:** This skill produces Markdown output only. It does not run CI commands, open browsers, push branches, or execute `git` commands on your behalf. Human-in-the-loop actions are listed as explicit checklist items.

> **Distinct from sextant:review-code:** Review evaluates code quality before merging. Ship prepares the logistics — changelog, PR description, version bump, and post-merge verification — for code that has already passed review.

---

## Complete Execution Workflow

### Step 1: Assess Change Scope

Read the diff and classify the changes:

**Change classification:**
- `bug fix` — corrects broken behavior, no new functionality
- `feature` — adds new user-visible capability
- `refactor` — restructures internals without behavior change
- `chore` — dependency updates, build config, tooling
- `breaking change` — removes or incompatibly changes a public interface

```
Change Scope Assessment
─────────────────────────────────────────────
Classification:           <bug fix / feature / refactor / chore / breaking change>
Files changed:            <count> files, ~<count> insertions, ~<count> deletions
Public interface changes: Yes (list) / No
Breaking changes:         Yes (list affected callers) / No
New dependencies:         Yes (list) / No
─────────────────────────────────────────────
```

### Step 2: Pre-Ship Checklist

Work through this checklist before generating the PR description. Items marked ❌ must be resolved before shipping; items marked ⚠️ should be resolved or explicitly accepted as known gaps.

```
Pre-Ship Checklist
─────────────────────────────────────────────────────
[ ] CHANGELOG entry written (or N/A for internal-only change)
[ ] Version bumped if this is a releasable unit
[ ] Breaking changes annotated with @deprecated or migration notes
[ ] No debug-only code left in (console.log, print, TODO: remove)
[ ] Public interface documentation updated (docstrings, README, OpenAPI spec)
[ ] Tests cover new behavior (link sextant:write-tests if coverage is missing)
[ ] No hardcoded credentials, tokens, or environment-specific values
[ ] No accidental file inclusions (build artifacts, .env files, IDE configs)
─────────────────────────────────────────────────────
```

### Step 3: Generate PR Description

Produce a structured PR description ready to paste:

```
─── PR Description ──────────────────────────────────

## Summary
<1–3 bullets: what this PR does, why it was needed, and the approach taken>

## Changes
<File-by-file or logically grouped list of what changed>

## Breaking Changes
<List each breaking change with the old and new interface signature.>
<If none: "None.">

## Testing
<How was this tested? What scenarios are covered? What is explicitly not covered?>

## Impact
<What systems, callers, or users are affected? Any deployment prerequisites?>
─────────────────────────────────────────────────────
```

### Step 4: Post-Merge Verification Checklist

After the PR merges, confirm these items manually:

```
Post-Merge Verification
─────────────────────────────────────────────────────
[ ] Public interfaces confirmed working in the target environment
[ ] Callers not covered by CI have been manually verified
[ ] Deployment configuration changes applied (env vars, feature flags, DB migrations)
[ ] Downstream consumers notified of breaking changes (if any)
[ ] Observability confirms new behavior is active (logs, metrics, alerts)
─────────────────────────────────────────────────────
```

---

## Forbidden Actions

- Do not run CI pipelines, push branches, or execute `git` commands
- Do not open pull requests, GitHub issues, or post to external services on the user's behalf
- Do not generate a CHANGELOG or version bump without reading the actual diff first — classification must come from the code, not assumptions

---

## Reply Format

Ship Summary:

| # | Item | Detail |
|---|------|--------|
| [1] | Change scope | <classification + file counts + breaking change status> |
| [2] | Pre-ship status | <N/N items passed ✅> / <items flagged ⚠️ with details> |
| [3] | PR description | <produced above> |
| [4] | Post-merge items | <checklist items requiring human action after merge> |
| [5] | Needs your input | <blocking gaps to resolve before merging> |
