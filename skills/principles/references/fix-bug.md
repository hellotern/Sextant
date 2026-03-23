# Bug Fix Workflow

> This file is loaded on demand by the `coding-principles` Skill when a bug fix task is identified. General coding principles (SOLID, DRY, baseline rules, etc.) are in the main SKILL.md and are not repeated here.

---

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

**🔗 GitNexus Enhanced — Quick call chain localization:**

Manual grep-based call chain tracing is slow and prone to missing indirect callers. Prioritize the following tools:

```
# 1. Get full context of the target function (callers, callees, execution process)
context({ symbol: "<function/class name where error occurs>" })

# 2. If you need to trace the complete execution flow (full path from entry to error location)
trace({ symbol: "<function name where error occurs>" })

# 3. If you only know the error keyword, use semantic search to locate the specific symbol first
query({ query: "<error message keyword or feature description>" })
```

**Usage strategy:**
- Use `context` first to see the list of callers for the erroring function, identifying the "bug exposure location"
- Then call `context` on each suspicious caller to trace upward to the "bug origin location"
- If the call chain is long, use `trace` to directly get the complete execution flow from entry point to target function
- The confidence scores returned by `context` help distinguish confirmed calls from possible calls

### Step 2: Impact Assessment

After locating the root cause, assess the potential impact of the fix:

- Which **callers** does this function/method have? Will their behavior change after the fix?
- Does the bug location involve a **public interface**? Will the fix change the interface contract?
- Is there other code that **depends on the bug's behavior**? (Sometimes bugs have existed so long that other code has adapted to the erroneous behavior)

**🔗 GitNexus Enhanced — Precise impact analysis:**

```
# Get all upstream code that depends on this function (who calls it, who will be affected if changed)
impact({ target: "<function/class name where bug is located>", direction: "upstream" })
```

The structure returned by `impact` contains:
- **Depth 1 (WILL BREAK)**: Direct callers — necessarily affected after the fix
- **Depth 2+ (MAY BREAK)**: Indirect callers with confidence scores
- **Cluster membership**: Which functional cluster this function belongs to, helping judge whether the impact crosses modules

Use `impact` results to fill in the impact assessment template below:

```
Bug Impact Assessment
─────────────────────────────────────────────
Bug location: <file/function name>
Root cause: <brief description>
Number of callers: <N> (🔗 returned by impact upstream)
Involves public interface: Yes / No
Possible code depending on buggy behavior: Yes (explanation) / No
Fix impact scope: Internal only / Affects callers / Cross-module (🔗 determined by cluster membership)
Risk level: Low / Medium / High
─────────────────────────────────────────────
```

**When risk level is "High" (involves public interface or cross-module), you MUST inform the user of the impact scope and confirm before fixing.**

### Step 3: Minimal-Change Fix

> ⚠️ **All principles in SKILL.md (SOLID, DRY, baseline rules, etc.) apply to every line of code written in this step — satisfy them as you write, not as an afterthought.**

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
    # Redesigned the discount calculation logic
    if not isinstance(price, (int, float)):  # Added type checking (not part of this bug)
        raise TypeError("...")
    if not isinstance(rate, (int, float)):   # Added type checking (not part of this bug)
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
[ ] Do related unit tests pass? If new tests are needed, hand off to write-tests.md
    with bug-fix context: root cause (Step 1) + impact scope (Step 2) already resolved.
    write-tests.md will start from the reproduction test, not from scratch.
[ ] Is the style consistent with surrounding code?
─────────────────────────────────────────────────────
```

**🔗 GitNexus Enhanced — Automate some checklist items:**

```
# "Does caller behavior still match expectations" → Re-query callers, compare with pre-fix impact results
impact({ target: "<fixed function name>", direction: "upstream" })

# "Does the fix introduce new boundary issues" → If already committed, use diff_review to analyze change impact
diff_review()
```

Checklist items that GitNexus can help verify:
- **Caller count consistency**: Compare Step 2 and current `impact` results to confirm nothing was missed
- **Dependency direction not broken**: `impact({ direction: "both" })` checks for newly introduced reverse dependencies
- **Cross-module impact controlled**: `impact` cluster information confirms the change hasn't spread to unexpected modules

Remaining checklist items (original bug reproduction, unit tests, style consistency) still require manual or test framework validation.

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

| Bug Pattern | Typical Manifestation | Investigation Direction | 🔗 GitNexus Assistance |
|-------------|----------------------|------------------------|------------------------|
| Null/None reference | `NoneType has no attribute` | Check if data source can be null/None | `context` to trace upstream data provider |
| Out-of-bounds access | `IndexError` / `KeyError` | Check collection length / key existence | `context` to find data structure definition |
| Concurrency race | Intermittent errors, data inconsistency | Check if shared state reads/writes are locked | `impact both` to find all readers/writers |
| Type mismatch | `TypeError` / implicit conversion error | Check type consistency across layers | `trace` to track cross-layer data flow |
| State leak | Previous call's state affects the next | Check for unreset global/class-level variables | `impact` to find all consumers of shared state |
| Missing boundary | Abnormal behavior for specific inputs | Check null, zero, negative, very large values | `context` to trace parameter origin |
| Async timing | Callback/Promise order doesn't match expectation | Check missing await, event order | `trace` to view full async execution path |
| Configuration error | Only occurs in specific environments | Check env vars, config file differences | `query` to search config-related code |

---

## Reply Format

End every bug-fix response with this block (omit a field only if it genuinely has nothing to report):

```
─── Fix Summary ─────────────────────────────────────────
① Conclusion:         <one sentence: root cause + fix approach + outcome>
② Changes:            <files / functions modified, with line ranges>
③ Risks / Assumptions: <caller assumptions made; edge cases not yet covered>
④ Verification:       <Step 4 checklist status; unit test pass / fail / not yet run>
⑤ Needs your input:   <high-risk callers to review; tests the user should run>
─────────────────────────────────────────────────────────
```
