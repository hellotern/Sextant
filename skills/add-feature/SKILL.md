---
name: sextant-add-feature
description: Use when implementing new functionality, new modules, new classes, or new API endpoints that do not yet exist in the codebase. Stronger signals: "add", "implement", "create", "build", "new feature", explicit new requirement. Use when the thing being built does not already exist. Apply this skill before starting any new-feature work.
---

!`awk 'f;/^---$/{c++}c==2{f=1}' ${CLAUDE_SKILL_DIR}/../principles/SKILL.md`

!`[ -d .gitnexus ] && awk 'f;/^---$/{c++}c==2{f=1}' ${CLAUDE_SKILL_DIR}/../tool-gitnexus/SKILL.md || true`

---

# New Feature / Module Workflow

## Core Principle

When adding new features, **integrate into the existing architecture like a native, not an outsider who starts from scratch**. New code should be fully consistent with existing code in style, structure, and interaction patterns.

---

## Complete Execution Workflow

### Step 1: Understand the Existing Architecture

Before starting, you must be able to answer the following questions:

**Architecture awareness:**
- What architectural pattern does the project use? (MVC / MVVM / Clean Architecture / Component-based / Microservices…)
- How are similar existing features implemented? (Find the best reference)
- What is the logic behind the project's directory structure? (By layer, by feature, by domain?)

**Positioning analysis:**
- Which layer does the new feature belong to? Where is its entry point?
- Which existing modules does the new feature need to depend on?
- Are there already extendable abstraction points (e.g., existing strategy interfaces, factory registries, event buses), or do new ones need to be created?

**Reference module:**
- Find **the most similar existing module** to the new feature as an implementation reference
- Observe its file structure, naming conventions, dependency injection approach, error handling patterns, and test organization
- The new module should follow the same patterns as closely as possible

🔗 When GitNexus is available, use `query` / `context` MCP tools for architecture exploration.

```
Pre-Implementation Research Checklist
─────────────────────────────────────────────
[ ] Understand the project architecture pattern and directory organization
[ ] Found the most similar reference module
[ ] Determined which layer the new feature belongs to
[ ] Determined the new feature's dependencies
[ ] Confirmed whether there are extendable abstraction points
[ ] Confirmed no overlap with responsibilities of existing modules
─────────────────────────────────────────────
```

### Step 2: Design the Solution

Before writing code, clarify the design:

**Location decision:**
- Place it at the same directory level as similar features
- If it's an entirely new domain, create a parallel structure referencing existing module directory structure

**Integration approach (priority order, high to low):**
```
Integration Strategy Priority
─────────────────────────────────────────────
1. Registry-based: Register with existing factory/registry/routing table → zero changes to existing code
2. Extension-point-based: Implement existing abstraction/strategy interface → add only, don't modify
3. Event-driven: Publish/subscribe via event bus → decoupled from existing modules
4. Config-driven: Enable new feature through config files → main flow is unaware
5. Invasive: Modify existing module code to integrate new feature → last resort
─────────────────────────────────────────────
```

**For large tasks, inform the user of:**
- Which integration approach is being used
- The responsibility boundary of the new module
- How it interacts with existing modules
- Expected file structure

Confirm before implementing.

### Step 2.5: TDD Mode — Write Contract Tests First (Medium / Large Tasks Only)

> **Skip this step for Lightweight tasks.** Only activate when the task scale is Medium or Large (per §3.2).

> **§P config check:** read `.sextant.yaml` before prompting.
> - `tdd: enforce` → skip the prompt; TDD is mandatory for all tasks
> - `tdd: default_on` → treat both Large and Medium as default Y
> - `tdd: off` or absent → use the scale-based defaults below

TDD mode: write contract tests first?
  **Large task → default Y** (opt out explicitly if not applicable)
  **Medium task → default n** (opt in if you want contract-first coverage)

**If Y:**
- Write **complete, runnable tests** for each new public interface: all three of Arrange, Act, and Assert — no `TODO` placeholders
- The Act calls the not-yet-implemented function or method directly; the test will fail because the implementation is absent or returns wrong output
- Valid red-light failure: `NameError` / `ImportError` / assertion on wrong return value
- Invalid "failure": syntax error, placeholder comment, test that cannot run at all — these are not TDD red tests
- Cover: 1 happy path, 1 null/boundary case, 1 error path
- These tests must fail **because the contract is not yet fulfilled** — that is the correct red state in red-green-refactor
- For full test writing guidance, link `sextant-write-tests`.

**If N (or Lightweight task):** Proceed directly to Step 3.

### Step 3: Implement — Follow Architecture Conventions

**Naming:** Fully consistent with the project's existing naming style (camelCase/snake_case, prefix/suffix conventions, abbreviation habits)

**Dependency direction:** Only upper layers depend on lower layers; reverse dependencies are not allowed. New modules must not introduce reverse dependencies.

**Interface protocol:** Interaction with existing modules must be consistent — if existing modules communicate through dependency injection, the new module uses dependency injection; if through event bus, use event bus.

**Extend, don't modify:** Prioritize OCP-compatible integration; avoid changing existing stable modules.

**Internal module structure:**
- Internal classes/functions are private by default; only expose necessary public interfaces
- Public interfaces must have explicit type declarations and parameter validation
- If the module needs to share data structures with other modules, place them in a dedicated shared layer

**Hollywood Principle:** New modules only declare dependencies (constructor injection / config registration) and do not proactively pull them.

```python
# ✅ Correct dependency approach for new module
class NewFeatureService:
    def __init__(self, repo: FeatureRepository, bus: EventBus):
        self._repo = repo
        self._bus = bus

# ❌ Incorrect dependency approach for new module
class NewFeatureService:
    def __init__(self):
        self._repo = MySQLFeatureRepository("localhost")  # Self-construct
        self._bus = EventBus.get_instance()                # Proactively pull
```

### Step 4: Architecture Compliance Audit (Required)

After completing the new module, run through an architecture audit:

```
New Module Architecture Audit Checklist
─────────────────────────────────────────────────────
[ ] Is the layering correct? No layer-crossing calls?
[ ] Has any circular dependency been introduced?
[ ] Has any existing module's boundary been violated? (No direct references to other modules' internal implementations)
[ ] Does the new module's responsibility overlap with existing modules?
[ ] Is the external interface consistent with project style? (Naming, parameter style, error handling)
[ ] Has any new global state or side effects been introduced?
[ ] Is the dependency direction compliant? Any reverse dependencies?
[ ] Does it follow the Hollywood Principle? (Dependencies injected, not pulled)
[ ] Does documentation / comments / type definitions / routing config need to be updated?
[ ] Does it need to be registered with existing factories / registries / config files?
─────────────────────────────────────────────────────
```

Audit results must be clearly communicated to the user: **Passed ✅** or **Issues found ⚠️ (with specific details)**.

---

## Common Pitfalls

| Pitfall | Description | Correct Approach |
|---------|-------------|-----------------|
| Responsibility overlap | New module implements functionality already covered by existing modules | Search for existing implementations first; prefer reusing or extending |
| Style break | New code is inconsistent with existing project style | Strictly reference the most similar existing module |
| Over-abstraction | New module only has one implementation yet introduces an abstraction layer | Follow YAGNI; abstract only when there's a second implementation |
| Implicit coupling | New module interacts with other modules through global variables or implicit conventions | All interactions through public interfaces or event bus |
| Missing registration | New module implemented but forgot to register with factory/routing/config | Audit checklist includes registration check |
| Reverse dependency | For "convenience," lower-layer module references higher-layer module | Strictly follow dependency direction rules |

---

## Sprint State Integration

If `.sextant/state.json` exists in the project root and the current task matches a sprint task:

- **On start:** offer to update the task's `status` from `pending` → `in_progress`. Ask: *"Update sprint state to mark Task N as in_progress?"*
- **On completion** (acceptance condition met): offer to update `status` to `done`. Ask: *"Update sprint state to mark Task N as done?"*
- **On blocker** (test failure, missing dependency, unresolvable ambiguity that halts progress): surface the issue, then ask: *"Mark Task N as blocked and record the reason in flags?"* If confirmed, set `status: "blocked"` and append `{"task": N, "reason": "<one-sentence blocker description>"}` to the top-level `flags` array. Do not proceed to the next task while a task is blocked.

Do not write the file without explicit user confirmation. If the user declines, continue without state updates.

---

## Reply Format

End every new-feature response with this block (omit a field only if it genuinely has nothing to report):

```
─── Feature Summary ─────────────────────────────────────
① Conclusion:         <one sentence: feature name + integration strategy used + outcome>
② Changes:            <new files created; existing files modified; registrations added>
③ Risks / Assumptions: <architectural assumptions; items not yet tested or integrated>
④ Verification:       <Step 4 architecture audit result: Passed ✅ / Issues ⚠️ (details)>
⑤ Needs your input:   <design decisions to confirm; manual registrations the user must handle>
─────────────────────────────────────────────────────────
```
