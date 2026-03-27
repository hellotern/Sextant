---
description: >-
  You MUST use this skill before starting multi-step implementation work when no ordered task breakdown exists yet.
  Use when the requirement is confirmed and clear, and you need to answer "how do we build this and in what order" — producing an ordered task list with skill assignments and acceptance criteria.
  Stronger signals: "plan this", "how should we build this", "break this into tasks", "sprint plan", "what order should we do this in", "create a task list", "what's the implementation sequence".
  Use sextant:refine-requirements first if the requirement itself is still ambiguous (that skill answers "what"; this skill answers "how and in what order").
  Use sextant:add-feature directly when the task is a single, well-scoped unit that needs no sequencing.
---

!../principles/SKILL_BODY.md

!../tool-gitnexus/SKILL_BODY.md

---

# Sprint Planning Workflow

## Core Principle

A plan is only as good as its dependency order. Tasks executed out of order produce integration failures that look like bugs but are actually sequencing errors. The goal is a **dependency-ordered task list where each task has a clear skill assignment, a bounded scope, and a single testable acceptance condition**.

> **Upstream skill:** `sextant:refine-requirements` answers "what to build" and produces a requirements confirmation document. This skill answers "how to build it and in what order." If requirements are still unclear or unconfirmed, use `sextant:refine-requirements` first.

---

## Complete Execution Workflow

### Session Resume Check

Before Step 1, check whether `.sextant/state.json` exists in the project root.

**If the file exists:** display the current sprint summary (requirement name, task statuses) and ask:
> "An existing sprint plan was found. Resume it, or start a new plan?"

- **Resume:** present the task list with current statuses; skip to the Execution Handoff section. Continue from the first `pending` or `in_progress` task.
- **New plan:** proceed with Steps 1–4 normally. Confirm with the user before overwriting the existing state.

**If the file does not exist:** proceed with Step 1 normally.

### Step 1: Parse Inputs

Accept either a requirements confirmation document (output of `sextant:refine-requirements`) or a clearly stated, unambiguous requirement. Extract:

- **Modules involved:** which existing modules will be modified or extended?
- **Entry points:** where does the new behavior surface (API endpoint, CLI command, UI trigger, event producer)?
- **Integration points:** where does the new code connect to existing code (interfaces, events, shared data structures, registries)?
- **Paradigm:** which architecture paradigm applies (per §6.0)? — determines the default layer ordering in Step 2.

🔗 When GitNexus is available, use `context` / `query` MCP tools to extract module relationships automatically.

### Step 2: Dependency Analysis

**Ordering rule:** lower-layer tasks must complete before higher-layer tasks that depend on them.

Default task ordering by paradigm (matches §6.2 dependency direction):

| Paradigm | Default Task Order |
|----------|--------------------|
| Backend layered | Data layer → Logic layer → Entry layer → Tests |
| Frontend component tree | Store / hooks → Feature components → Page → Tests |
| CLI / Script | Core logic → Command handlers → CLI entry → Tests |
| Functional (FP) | Pure core functions → I/O adapters → Entry → Tests |
| Monorepo | Shared packages → Domain packages → App packages → Tests |
| Event-driven | Schema / event contracts → Producers → Consumers → Integration tests |
| Serverless | Core logic → Handler functions → Infrastructure config → Tests |
| AI/ML pipeline | Data pipeline → Preprocessing → Model → Evaluation → Serving |

**Cross-task data dependencies:** if Task B consumes the output or interface produced by Task A, Task A must be sequenced first — regardless of layer.

**Conflict arbitration:** when ordering is ambiguous, apply §5.5 arbitration rules. When a task touches a public interface, treat it as at least Medium scale and confirm before sequencing.

### Step 3: Task Specification

For each task, specify all six fields:

1. **Title:** one action verb + one noun (e.g., "Add `UserRepository.findByEmail` method")
2. **Skill:** which sextant sub-skill handles this task?
   - New code → `sextant:add-feature`
   - Change existing → `sextant:modify-feature`
   - Multi-module coordinated change → `sextant:migrate`
   - Tests → `sextant:write-tests`
   - Unclear requirements → `sextant:refine-requirements`
3. **Scale:** apply the Impact Radius Scorecard (§3.2) — Lightweight / Medium / Large
4. **Files:** likely files to create or modify
5. **Depends on:** list of task IDs that must complete first, or "None"
6. **Acceptance:** a single, testable condition confirming the task is done

**Acceptance condition format:** `Given <precondition>, when <action>, then <verifiable outcome>.`
One sentence — if it requires more, the task scope is too large and should be split.

**Scale gate:** if any task scores as Architectural (Impact Radius 9–10), flag it for decomposition before proceeding. Do not plan an Architectural task as a single unit.

### Step 4: Output the Plan

```
─── Sprint Plan ─────────────────────────────────────
Requirement: <name / one-sentence description>
Paradigm:    <detected paradigm>

Task 1: <title>
  Skill:       <sextant skill name>
  Scale:       <Lightweight / Medium / Large> (Impact radius: N)
  Files:       <likely files to create or modify>
  Depends on:  None / Task N, Task M
  Acceptance:  Given <precondition>, when <action>, then <verifiable outcome>.

Task 2: <title>
  Skill:       ...
  Scale:       ...
  Files:       ...
  Depends on:  ...
  Acceptance:  ...

Suggested sequence: 1 → 3 → 2 → 4 → 5
Rationale: <one sentence explaining any non-obvious ordering decisions>
─────────────────────────────────────────────────────
```

### Execution Handoff

After the user confirms the sprint plan, this skill transitions from planner to pipeline entry point. Immediately offer to begin execution:

```
─── Ready to Execute ────────────────────────────────
The plan is confirmed. Suggested starting point:

Task 1: <title>
  → Invoke: sextant:<skill>
  → To begin, describe the task to me and I will apply the <skill> workflow.

When Task 1 is complete, Task 2 becomes unblocked:
  → Invoke: sextant:<skill>

Continue in sequence: <1 → 2 → ...>
─────────────────────────────────────────────────────
```

**Flow rules for execution:**
- Each task handoff is a fresh skill invocation — the executing skill owns its own workflow from that point
- If a task reveals a blocking issue (test failure, missing dependency, ambiguous requirement), pause execution and surface it before moving to the next task
- If a task's scope expands beyond its planned scale during execution, re-assess the Impact Radius before proceeding — it may affect downstream task ordering
- Tasks with no mutual dependencies can be executed in parallel if the user has multiple working contexts

**State persistence (optional):**

To resume this sprint across sessions, ask the user: *"Save sprint state to `.sextant/state.json` so we can resume later?"*

If the user confirms, write the file:

```json
{
  "version": "1",
  "sprint": {
    "requirement": "<one-sentence requirement name>",
    "tasks": [
      {
        "id": 1,
        "title": "<title>",
        "skill": "sextant:<skill>",
        "scale": "Lightweight | Medium | Large",
        "status": "pending | in_progress | done | blocked",
        "depends_on": [],
        "acceptance": "<testable condition>",
        "flags": []
      }
    ],
    "suggested_sequence": [1, 2, 3]
  },
  "flags": []
}
```

Update the relevant task's `status` field as tasks complete:
- `pending` → `in_progress` when a task begins
- `in_progress` → `done` when its acceptance condition is met
- `in_progress` → `blocked` if a blocking issue is surfaced

**Do not write `.sextant/state.json` without explicit user confirmation.** Automatic writes are forbidden.

---

## Forbidden Actions

- Do not assign vague acceptance criteria ("works correctly", "looks good") — every condition must be testable without interpretation
- Do not output an unordered list of tasks and call it a plan — dependency order is the core deliverable
- Do not plan a task that scores Architectural without first flagging it for decomposition
- Do not begin planning if the requirement still has unresolved 🔴 gaps — resolve them via `sextant:refine-requirements` first

---

## Reply Format

Prepend the Sprint Plan block with a one-line summary:

```
Planning complete: <N> tasks, suggested sequence: <1 → 2 → ...>, scales: <N Lightweight, N Medium, N Large>.
```

Then output the full Sprint Plan block.
