---
description: >-
  You MUST use this skill before changing, enhancing, or refactoring any existing functionality.
  Use when the code already exists and you are altering its behavior, performance, or structure — not fixing a bug.
  Stronger signals: "modify", "refactor", "optimize", "improve", "change how X works", "enhance", "update the logic".
  Use sextant:add-feature instead when the thing being built does not yet exist.
  Use sextant:fix-bug instead when the existing behavior is broken and needs to be restored.
---

!../principles/SKILL_BODY.md

!../tool-gitnexus/SKILL_BODY.md

---

# Modify Existing Feature / Module Workflow

## Disambiguating modify-feature vs fix-bug

> **Use this skill when:** the code does X correctly — you want it to do Z instead (desired behavior is changing).
> **Use fix-bug when:** the code *should* do X but does Y — you want to restore correct behavior.
>
> Quick test: *"Is the current behavior broken, or just not what we want going forward?"*
> → **Broken / was never right** → **stop**. Tell the user: "This looks like a bug rather than a behavior change — the fix-bug workflow is a better fit. You can say something like 'this is broken / it used to work' to trigger the right workflow, or tell me to proceed anyway and I'll apply baseline rules only." Do not proceed unless the user explicitly says to proceed.
> → **Worked correctly, requirements evolved** → modify-feature (continue here).
>
> Edge case: Performance problems and security gaps feel like bugs but are almost always modify-feature — the code "works," it just doesn't meet a non-functional requirement. Continue with this skill.

## Core Principle

Modification requests are riskier than additions — you're touching a running system; pulling one thread affects the whole. The core strategy is **understand first, analyze, then refine, and only then act**.

---

## Complete Execution Workflow

> **Progress tracking:** At the start of each applicable step, output an updated progress block. Include **only the steps that apply to the current task scale** — omit inapplicable steps entirely:
> - **Lightweight**: Step 5 only
> - **Medium**: Steps 1, 5, 6 (Step 3 optional — include if you run it)
> - **Large**: All steps (1 → 2 → 3 → 4 → 5 → 6)
>
> Large-task example (adapt by removing rows for smaller scales):
> ```
> Modify Feature Progress
> → Step 1: Read & Establish Context  — in progress
> ○ Step 2: Impact Analysis
> ○ Step 3: Requirements Refinement
> ○ Step 4: Solution Design + Confirm
> ○ Step 5: Implement
> ○ Step 6: Compliance Audit
> ```
>
> Replace `○` with `→` for the current step, and `✓` once complete.

---

### Step 1: Read the Code — Establish Full Context

> Required for medium and above tasks. Lightweight tasks (minor single-function adjustments) can be simplified to just reading the target function itself.

Before acting, you must build a complete understanding of the target code and its surroundings.

**Questions to answer:**
- What is the **responsibility boundary** of the target code? Which layer does it belong to?
- What are its **callers**? (Who uses it — trace upward)
- What are its **dependencies**? (What does it use — trace downward)
- Is it **indirectly depended upon by other modules via events/callbacks/interfaces**?
- What is the **design intent** of the current code? (Read comments, commit messages, PR descriptions)
- Are there **implicit contracts**? (e.g., return value format, call order, state assumptions)

🔗 When GitNexus is available, use `context` MCP tool to get callers and callees automatically.

```
─── Reading Scope (must cover) ──────────────────────
[ ] Complete implementation of the target function/class/module itself
[ ] Direct callers (at least one level up)
[ ] Direct dependencies (at least one level down)
[ ] Related interface definitions / abstract base classes / type declarations
[ ] Related config items / constant definitions
[ ] Related unit tests / integration tests (if any)
─────────────────────────────────────────────────────
```

### Step 2: Impact Analysis — Map the Change Radiation

> Required when involving public interfaces, cross-module changes, or shared data structures.

**Analysis dimensions:**
- **Direct impact**: Behavioral changes to the modified function/class itself
- **Upstream impact**: Do callers depend on the behavior that is about to change?
- **Downstream impact**: Does the way dependencies are used need to be adjusted synchronously?
- **Cross-module impact**: Are other modules associated through event bus, shared state, or shared DTOs?
- **Contract impact**: Do the interface signature, parameter types, or return structure change (Breaking Change)?
- **Data impact**: Does it involve database schema changes, cache invalidation, or data migration?

🔗 When GitNexus is available, use `impact` MCP tool for upstream/downstream analysis.

```
─── Change Impact Analysis Report ───────────────────
Change target: <module/function name>
Change type: [ ] Behavior modification  [ ] Signature change  [ ] Internal refactor  [ ] Extension enhancement

Direct impact scope:
  - <list modified files/functions>

Indirect impact scope:
  - <list affected callers/dependents>

Is it a Breaking Change: Yes / No
Does it require synchronous changes to other modules: Yes (list) / No
Does it involve data changes: Yes (describe) / No
Risk level: Low / Medium / High
─────────────────────────────────────────────────────
```

### Step 3: Requirements Refinement — Re-examine Under Architecture Constraints

Don't directly implement after receiving requirements — use the established code context to validate and refine them.

**Questions to confirm:**
- In the current architecture, where is **the most natural implementation point** for the behavioral change?
- Can the requirements be achieved through **extending existing abstraction points**, or must core logic be modified?
- Do the requirements conflict with existing design intent?
- Are the boundary conditions of the requirements clear?

**Core principle: Prioritize finding an "extension-based modification" path; only then consider "invasive modification."**

```
─── Modification Strategy Priority (best to worst) ──
1. Configuration: Modifying config/params is sufficient → zero code changes
2. Extension: Add implementation class/strategy/handler, register with existing extension point → don't touch old code
3. Decoration: Wrap existing behavior with decorator/middleware/AOP → old code is unaware
4. Local modification: Modify logic inside existing function/method → minimal change principle
5. Signature change: Need to modify interface/parameters/return value → must synchronize all callers
6. Structural reorganization: Need to split/merge/move modules → requires explicit user authorization
─────────────────────────────────────────────────────
```

### Step 4: Solution Design — Create Modification Plan and Get Confirmation

> Confirm first when involving public interfaces, cross-module changes, or Breaking Changes.

```
─── Modification Plan ───────────────────────────────
Requirement summary: <one-sentence description>
Modification strategy: <Configuration / Extension / Decoration / Local modification / Signature change / Structural reorganization>

Change list:
  1. <File A> - <change description>
  2. <File B> - <change description>

Impact scope: <directly/indirectly affected modules>
Breaking Change: Yes / No
Risk points: <if any>

Confirm execution?
─────────────────────────────────────────────────────
```

### Confirmation Gate (between Step 4 and Step 5)

After presenting the Modification Plan, **before writing any code**, call `AskUserQuestion` with:

- **question**: The Modification Plan block above
- **options**:
  - `"Yes, proceed with implementation"`
  - `"No — let's revise the approach"`

**Decision rules by risk level:**

| Risk | Behavior |
|------|----------|
| **High** (Breaking Change, cross-module, or Structural reorganization) | Always call `AskUserQuestion`. Do not touch any file until user selects "Yes". |
| **Medium** (multi-file, internal-only, no Breaking Change) | Always call `AskUserQuestion`. Do not touch any file until user selects "Yes". |
| **Low** (Lightweight, single-function config or local change) | Skip — proceed directly to Step 5. |

**If user selects "No":** ask *"What direction would you prefer?"*, revise the Modification Plan, and call `AskUserQuestion` again before proceeding.

---

### Step 4.5: TDD Mode — Baseline + Contract Tests (Large Tasks Only)

> **Large tasks only.** Run after the modification plan is confirmed in Step 4, before writing any implementation code.

> **§P config check:** read `.sextant.yaml` before prompting.
> - `tdd: enforce` → skip the prompt; TDD is mandatory
> - `tdd: default_on` → treat as default Y
> - `tdd: off` or absent → use the default below

TDD mode: write regression baseline and contract tests first? [Y/n]  (default Y — opt out explicitly if this is a structural-only refactor with no behavior change)

**If Y:**
1. **Regression baseline:** Write **complete, runnable tests** that capture the **current** behavior before touching any code. These tests must pass right now, and must continue to pass after the change is complete. They are your regression safety net.
2. **New behavior contracts:** Write **complete, runnable tests** for the new behavior (Arrange + Act + Assert — no `TODO` placeholders). The Act calls the existing function with inputs that should produce the new output — the test fails because the implementation does not yet satisfy the new contract. Valid red-light failure: assertion on wrong return value, raised exception where none was expected, or vice versa. An incomplete test that cannot run is not a valid red.
- For full test writing guidance, link `sextant:write-tests`.

**If N (or Lightweight task):** Proceed directly to Step 5.

### Step 5: Implement — Follow the Minimal Change Principle

**Execution discipline:**
- **Maintain style consistency**: Naming, indentation, comment language fully consistent with surrounding code
- **No hitchhiking**: Don't "optimize" unrelated code while implementing requirements
- **Changes are traceable**: Format: `# change: <requirement description> - <reason for change>`
- **Backward compatibility**: Prefer compatible approaches (default parameters, overloading, adapters) unless user explicitly states otherwise
- **Incremental implementation**: Do structural adjustments first, then behavioral changes

**Common backward compatibility approaches:**
```python
# ✅ Add optional parameter, old calling style unaffected
def process_order(order_id: str, priority: int = 0):  # priority is newly added
    ...

# ✅ Keep old function as adapter, internally calls new implementation
def get_user(user_id):                    # Old interface, preserved
    return get_user_v2(user_id).to_legacy_format()
```

**❌ Forbidden actions:**
- Modifying public interface signatures without confirmation
- Sneaking in "optimizations" unrelated to the current requirement
- Deleting code that's temporarily unused without informing the user
- Changing return value structures without updating all callers

### Step 6: Compliance Audit (Required for Medium and Above Tasks)

```
─── Modification Architecture Audit Checklist ───────
[ ] Does the change follow the minimal change principle? Any unnecessary extra changes?
[ ] Is style consistency with surrounding code maintained?
[ ] Has the existing interface contract been broken? (Parameters, return values, exceptions)
[ ] Have all callers been adapted to the change? Any missed?
[ ] Has any new circular dependency been introduced?
[ ] Has the encapsulation boundary of existing modules been broken?
[ ] Is the dependency direction still compliant? Any new reverse dependencies?
[ ] Are there conflicts with adjacent features? (Shared state, events, shared data structures)
[ ] Do the original unit tests still pass? Do tests need to be updated?
[ ] Does documentation / comments / type definitions / CHANGELOG need to be updated?
─────────────────────────────────────────────────────
```

---

## Workflow Tailoring by Task Scale

**Lightweight** (minor single-function logic adjustment, config changes, style fixes):
- Required: Step 5 only
- Optional: Step 1 (quick scan)
- Skip: Steps 2–4, Step 4.5, Step 6

**Medium** (modify module internal logic, add/remove internal functions):
- Required: Step 1 → Step 5 → Step 6
- Optional: Step 3
- Skip: Steps 2, 4, Step 4.5

**Large** (cross-module changes, public interface modifications, Breaking Changes):
- Required: Steps 1 → 2 → 3 → 4 → 5 → 6 in order
- Optional: Step 4.5 (TDD mode, default Y) — runs after Step 4 confirmation, before Step 5

> Step 4.5 (TDD mode) is only meaningful after Step 4 confirms the modification plan. It is never run before Step 4, and never run on Lightweight tasks.

---

## Common Pitfalls

| Pitfall | Description | Correct Approach |
|---------|-------------|-----------------|
| Act without reading | Modified function without reading callers | At minimum trace one level up |
| Hitchhiking | Smuggled in "opportunistic optimizations" | Strict separation: change only serves the current requirement |
| Implicit Breaking Change | Changed return value structure assuming callers unaffected | Proactively check all callers |
| Over-modification | User requested minor adjustment but entire module was rewritten | Follow minimal change principle |
| Forgot compatibility | Directly changed signature when modifying public interface | Prefer default parameters/overloading |
| Missed sync | Changed code but forgot to update related docs/types/tests | Audit checklist covers sync items |

---

## Sprint State Integration

If `.sextant/state.json` exists in the project root and the current task matches a sprint task:

- **On start:** offer to update the task's `status` from `pending` → `in_progress`. Ask: *"Update sprint state to mark Task N as in_progress?"*
- **On completion** (acceptance condition met): offer to update `status` to `done`. Ask: *"Update sprint state to mark Task N as done?"*
- **On blocker** (test failure, missing dependency, unresolvable ambiguity that halts progress): surface the issue, then ask: *"Mark Task N as blocked and record the reason in flags?"* If confirmed, set `status: "blocked"` and append `{"task": N, "reason": "<one-sentence blocker description>"}` to the top-level `flags` array. Do not proceed to the next task while a task is blocked.

Do not write the file without explicit user confirmation. If the user declines, continue without state updates.

---

## Reply Format

**Lightweight task** (single-function logic change, config update, style fix): one sentence only.
```
✅ Modified `<function>`: <what changed> using <strategy> (<file>:<line>).
```

**Medium/large task** (cross-file, public interface, or Breaking Change): full block.

Modification Summary:

| # | Item | Detail |
|---|------|--------|
| [1] | Conclusion | <one sentence: what changed, which strategy was used, and the outcome> |
| [2] | Changes | <files / functions modified; callers updated; backward-compat shims added> |
| [3] | Risks / Assumptions | <Breaking Change status; compatibility assumptions; callers not yet adapted> |
| [4] | Verification | <Step 6 audit result: Passed ✅ / Issues ⚠️ (details); unit test status> |
| [5] | Needs your input | <Breaking Change approval; callers that must still be updated by the user> |
