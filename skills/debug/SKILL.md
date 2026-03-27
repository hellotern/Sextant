---
description: >-
  You MUST use this skill before reading any code or proposing any fix when the bug location is unknown.
  Use when you have a symptom (error, crash, unexpected output) but cannot yet point to the specific function or line where it originates.
  Stronger signals: "I don't know where this is coming from", "can't reproduce consistently", "something is wrong but I don't know where", intermittent failures, no stack trace.
  Use sextant:fix-bug instead when you CAN already point to the specific file or line causing the bug.
---

!../principles/SKILL_BODY.md

!../tool-gitnexus/SKILL_BODY.md

---

# Debugging Workflow

## Disambiguation Gate

> **Before starting:** Can you point to a specific function or line and say "the bug is here"?
> → **Yes** → Stop. Use `sextant:fix-bug` — the location is known, that skill handles the fix.
> → **No** → Continue here. This skill is for "symptom known, location unknown."

## Core Principle

Debug by **bisection, not inspection**. Form a hypothesis about which boundary separates correct from incorrect behavior, then eliminate layers until only the root cause remains.

---

## Complete Execution Workflow

### Step 1: Capture the Symptom

Before forming any hypothesis, establish a precise symptom record:

- **Error message** (exact text, stack trace if available)
- **Reproduction steps** (what sequence of actions triggers it?)
- **Frequency** (always / intermittent / environment-specific)
- **Regression** (did this ever work? What changed recently?)

```
─── Symptom Record ──────────────────────────────────
Error / unexpected output: <exact message or behavior>
Trigger steps:             <reproducible sequence>
Frequency:                 Always / Intermittent (~X%) / Specific environment only
Regression:                Yes (last known good: <commit/date>) / No / Unknown
─────────────────────────────────────────────────────
```

### Step 2: Identify Paradigm + Select Isolation Strategy

Identify which architecture paradigm applies (per §6.0), then use the corresponding isolation strategy:

| Paradigm | Isolation Direction | Isolation Technique |
|----------|---------------------|---------------------|
| **Backend layered** | Entry → Logic → Data (inward) | Add logging at each layer boundary; find the first layer that returns incorrect data |
| **Frontend component tree** | Page → Feature → Atom (downward) | Props injection test: pass hardcoded data directly to component, bypass store |
| **CLI / Script** | Entry → Command handler → Core logic (inward) | Print intermediate values at each function boundary |
| **Functional (FP)** | I/O boundary → Pure core (inward) | Test pure functions in isolation; side effects confined to boundaries |
| **Concurrent / Async** | Reconstruct timing diagram; locate shared state | Add timestamps/sequence numbers to logs; inspect lock points on shared state |
| **Event-driven** | Trace event publish → handler chain | Log each consumed event; verify handler receives correct payload |

🔗 When GitNexus is available, use `context` / `trace` MCP tools to map the call chain automatically.

### Step 3: Form and Validate Hypotheses

**Bisection protocol:** Find the boundary between "working correctly" and "already wrong."

1. Identify the layer / module where the symptom surfaces — this is the **observation point**
2. Ask: "Is the input to this layer already wrong, or does this layer corrupt correct input?"
3. Move the observation point inward (toward the source) until you find the first layer that produces incorrect output
4. That boundary is your root cause hypothesis

**For intermittent bugs (concurrency / async):**
- Add sequence numbers or timestamps to logs before the symptom point
- Identify the shared state that changes between passing and failing runs
- Hypothesis format: `"Thread A reads X before Thread B writes the updated value"`

**For environment-specific bugs:**
- List all environmental differences (OS, config, versions, data state)
- Eliminate variables one by one until the failing condition is isolated

```
─── Hypothesis Log ──────────────────────────────────
Hypothesis 1: <the bug is in X because Y>
  Test:   <what to check / add / isolate>
  Result: ✅ Confirmed / ❌ Eliminated / ⏳ Pending

Hypothesis 2: ...
─────────────────────────────────────────────────────
```

**Hypothesis limit gate — trigger when 3+ hypotheses have been eliminated without confirming root cause:**

Stop the bisection loop. Do not generate more hypotheses. Instead, choose one of the following escalation paths:

1. **Request more context** — ask the user for: a minimal reproduction case, relevant logs or stack traces at the failure point, or the last known-good commit/state
2. **Suggest `git bisect`** — if the bug is a regression with an unknown introduction point, `git bisect` identifies the exact commit; ask the user to run it and share the result
3. **Add structured logging** — propose specific log statements at the current observation point boundary; ask the user to re-run and share the output before resuming bisection
4. **Widen the symptom map** — if only one symptom was captured, ask whether the bug manifests differently under other conditions (different inputs, environments, users)

```
─── Escalation Decision ─────────────────────────────
Hypotheses eliminated: N
Root cause: ⏳ not yet confirmed
Escalation chosen: <context request / git bisect / structured logging / symptom widening>
Information needed from user: <specific artifact or action>
─────────────────────────────────────────────────────
```

### Step 4: Confirm Root Cause → Hand Off to Fix

When you can answer all three:
1. **Which function / line** produces the incorrect output?
2. **Under what exact input or state** does the failure occur?
3. **Why** does that code produce incorrect output (logic error, missing guard, race condition, wrong assumption)?

→ Root cause is confirmed. **Hand off: switch to `sextant:fix-bug`.**

Provide the fix-bug workflow with pre-filled context:
- Root cause location (file + function)
- Trigger conditions
- Impact scope already identified (skip fix-bug Step 2 if already covered here)

---

## Forbidden Actions

- Do not apply a workaround (`try/except` swallowing, hardcoded fallback value) before the root cause is confirmed — this hides the bug
- Do not generate a list of all possible causes without narrowing — work by elimination, not enumeration
- Do not start fixing while the location is still uncertain — confirm first, then hand off to `sextant:fix-bug`

---

## Reply Format

Debug Summary:

| # | Item | Detail |
|---|------|--------|
| [1] | Symptom | <exact error + reproduction conditions + frequency> |
| [2] | Paradigm | <detected paradigm> → isolation strategy: <strategy name> |
| [3] | Hypotheses tested | <list with ✅ Confirmed / ❌ Eliminated result for each> |
| [4] | Root cause | <file:function — what and why> / ⏳ Not yet confirmed (next step: <action>) |
| [5] | Next action | Switch to sextant:fix-bug with pre-filled context / <specific investigation step> |
