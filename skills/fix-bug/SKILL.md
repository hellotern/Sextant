---
description: >-
  Use when the user is fixing a bug, error, crash, regression, or unexpected behavior in existing code. Stronger signals: error messages, stack traces, "not working", "broken", "failing", "it used to work". Apply this skill before starting any bug-fix work.
---

!`python3 ${CLAUDE_SKILL_DIR}/../principles/strip_frontmatter.py ${CLAUDE_SKILL_DIR}/../principles/SKILL.md`

!`python3 ${CLAUDE_SKILL_DIR}/../principles/strip_frontmatter.py ${CLAUDE_SKILL_DIR}/../tool-gitnexus/SKILL.md --if-dir-exists .gitnexus`

---

# Bug Fix Workflow

## Disambiguating fix-bug vs modify-feature

> **Use this skill when:** the code *should* do X but does Y — you want to restore correct behavior.
> **Use modify-feature when:** the code does X correctly — you want it to do Z instead (desired behavior changed).
>
> Quick test: *"Did this ever work correctly, or was it always intended to work differently?"*
> → **Yes, it used to work / should work** → fix-bug (continue here).
> → **No, the requirement itself is changing** → **stop**. Tell the user: "This looks like a behavior change rather than a bug fix — the modify-feature workflow is a better fit. You can say something like 'refactor/change how X works' to trigger the right workflow, or tell me to proceed anyway and I'll apply baseline rules only." Do not proceed unless the user explicitly says to proceed.
>
> Edge case: A feature never implemented but expected is a bug only if it was promised in an interface contract; otherwise **stop** and direct the user to `sextant:add-feature`.

## Core Principle

When fixing bugs, **make surgical modifications to the existing solution** — do not start over with a rewrite.

---

## Complete Execution Workflow

### Step 1: Reproduce and Locate the Root Cause

Before making any changes, confirm:

- What is the **specific manifestation** of the bug? (Error message, abnormal behavior, data anomaly)
- What are the **trigger conditions**? (Specific input, timing, environment)
- Where is the **root cause**? (Don't fix the symptom — find the source)

**Localization techniques:**
- Starting from the error manifestation, trace the call chain **upward** to the earliest point of failure
- Distinguish between "where the bug is exposed" and "where the bug originates" — they are often not the same place
- Check whether **implicit state assumptions** have been violated (e.g., a variable expected to be non-null is actually null)
- Pay attention to **boundary conditions**: null values, zero values, overflow, concurrency races, type mismatches

🔗 When GitNexus is available, use `context` / `trace` MCP tools for enhanced root-cause tracing.

### Step 2: Impact Assessment

After locating the root cause, assess the potential impact of the fix:

- Which **callers** does this function/method have? Will their behavior change after the fix?
- Does the bug location involve a **public interface**? Will the fix change the interface contract?
- Is there other code that **depends on the bug's behavior**? (Sometimes bugs have existed so long that other code has adapted to the erroneous behavior)

🔗 When GitNexus is available, use `impact` MCP tool to enumerate callers automatically.

```
Bug Impact Assessment
─────────────────────────────────────────────
Bug location: <file/function name>
Root cause: <brief description>
Number of callers: <N>
Involves public interface: Yes / No
Possible code depending on buggy behavior: Yes (explanation) / No
Fix impact scope: Internal only / Affects callers / Cross-module
Risk level: Low / Medium / High
─────────────────────────────────────────────
```

**When risk level is "High" (involves public interface or cross-module), you MUST inform the user of the impact scope and confirm before fixing.**

### Step 3: Minimal-Change Fix

**Execution discipline:**
- **Only change the part of code that causes the bug** — do not expand the scope of changes
- **Maintain style consistency**: The fix code is fully consistent with surrounding code style (naming, indentation, comment language)
- **Annotate changes**: Comments explaining the fix reason, format: `# fix: <reason description>`
- **No hitchhiking**: Don't "optimize" unrelated code while fixing a bug — this introduces new regression risk

**✅ Correct fix approach:**
```python
def calculate_discount(price, rate):
    # fix: rate = 0 causes division by zero; added boundary check
    if rate <= 0:
        return price
    return price / rate
```

**❌ Incorrect fix approach:**
```python
# Rewrote the entire function — introduces unnecessary change risk
def calculate_discount(price, rate):
    if not isinstance(price, (int, float)):  # Added type checking (not part of this bug)
        raise TypeError("...")
    validated_rate = max(rate, 0.01)          # Changed boundary strategy (not the original behavior)
    return round(price / validated_rate, 2)   # Added rounding (not part of this bug)
```

### Step 4: Boundary Validation

After completing the fix, check:

```
Fix Verification Checklist
─────────────────────────────────────────────────────
[ ] Is the original bug fixed? (Verify with original trigger conditions)
[ ] Is the normal path still correct? (Regression validation)
[ ] Are related boundary conditions handled correctly? (Null, zero, extreme values)
[ ] Does the fix introduce new boundary issues?
[ ] Does caller behavior still match expectations?
[ ] Do related unit tests pass? If new tests are needed, use the sextant:write-tests skill
    with bug-fix context: root cause (Step 1) + impact scope (Step 2) already resolved.
[ ] Is the style consistent with surrounding code?
─────────────────────────────────────────────────────
```

Report to the user: **Fix complete ✅** or **Additional issues found ⚠️ (with description)**.

---

## Forbidden Actions

- Delete the old function and write a new "better" replacement (unless the user explicitly requests refactoring)
- "Optimize" unrelated code while fixing a bug (introduces new variables, increases regression risk)
- Use a temporary patch to work around the problem without fixing the root cause (e.g., adding `try/except` to swallow the exception)
- "Mask" the bug with defensive code without understanding the root cause

---

## Exceptions (Require Explicit User Authorization)

The following situations can break the "minimal change" principle, but **must be initiated by the user**:
- User says "this approach has fundamental flaws, try a different approach"
- User says "redesign this module/component"
- User says "refactor this part of the code while you're at it"

Even when the user authorizes expanding the scope, **fix the bug first, then refactor** — do it in separate steps, don't mix them together.

---

## Common Bug Pattern Quick Reference

| Bug Pattern | Typical Manifestation | Investigation Direction |
|-------------|----------------------|------------------------|
| Null/None reference | `NoneType has no attribute` | Check if data source can be null/None |
| Out-of-bounds access | `IndexError` / `KeyError` | Check collection length / key existence |
| Concurrency race | Intermittent errors, data inconsistency | Check if shared state reads/writes are locked |
| Type mismatch | `TypeError` / implicit conversion error | Check type consistency across layers |
| State leak | Previous call's state affects the next | Check for unreset global/class-level variables |
| Missing boundary | Abnormal behavior for specific inputs | Check null, zero, negative, very large values |
| Async timing | Callback/Promise order doesn't match expectation | Check missing await, event order |
| Configuration error | Only occurs in specific environments | Check env vars, config file differences |

---

## Sprint State Integration

If `.sextant/state.json` exists in the project root and the current task matches a sprint task:

- **On start:** offer to update the task's `status` from `pending` → `in_progress`. Ask: *"Update sprint state to mark Task N as in_progress?"*
- **On completion** (acceptance condition met): offer to update `status` to `done`. Ask: *"Update sprint state to mark Task N as done?"*
- **On blocker** (test failure, missing dependency, unresolvable ambiguity that halts progress): surface the issue, then ask: *"Mark Task N as blocked and record the reason in flags?"* If confirmed, set `status: "blocked"` and append `{"task": N, "reason": "<one-sentence blocker description>"}` to the top-level `flags` array. Do not proceed to the next task while a task is blocked.

Do not write the file without explicit user confirmation. If the user declines, continue without state updates.

---

## Reply Format

**Lightweight task** (single function, < 50 lines changed): one sentence only.
```
✅ Fixed `<function>`: <root cause> — <what changed> (<file>:<line>).
```
or if something needs attention:
```
⚠️ Fixed `<function>`: <root cause> — <what changed>. Note: <one risk or open question>.
```

**Medium/large task** (cross-file, public interface, or high-risk): full block.

Fix Summary:

| # | Item | Detail |
|---|------|--------|
| [1] | Conclusion | <one sentence: root cause + fix approach + outcome> |
| [2] | Changes | <files / functions modified, with line ranges> |
| [3] | Risks / Assumptions | <caller assumptions made; edge cases not yet covered> |
| [4] | Verification | <Step 4 checklist status; unit test pass / fail / not yet run> |
| [5] | Needs your input | <high-risk callers to review; tests the user should run> |
