---
description: >-
  You MUST use this skill before evaluating, commenting on, or giving feedback on any code.
  Use when the primary request is to assess existing code — quality, correctness, style, or readiness to merge.
  Stronger signals: "review", "PR", "pull request", "code review", "check this code", "is this correct", "review this file", "give me feedback on", "look at this diff".
  Takes highest priority when the primary request is to evaluate code rather than write or fix it.
  Use sextant:security instead when the review focus is specifically on security vulnerabilities.
---

!`python3 ${CLAUDE_SKILL_DIR}/../principles/strip_frontmatter.py ${CLAUDE_SKILL_DIR}/../principles/SKILL.md`

!`python3 ${CLAUDE_SKILL_DIR}/../principles/strip_frontmatter.py ${CLAUDE_SKILL_DIR}/../tool-gitnexus/SKILL.md --if-dir-exists .gitnexus`

---

# Code Review Workflow

## Core Principle

The goal of code review is not to find fault, but to **discover design flaws, logic vulnerabilities, and architecture risks before code is merged**. Review quality depends on the reviewer's depth of understanding of the change context — the deeper the understanding, the more fundamental the issues found.

---

## Before You Start

### Operating Mode — Declare Before Starting

**Before reading a single line of code, output this declaration as the first line of your response:**

```
Mode: Review-only  — reason: <one phrase>
```
or
```
Mode: Review+patch — reason: <one phrase>
```

**Mode selection rules:**

| Signal | Mode |
|--------|------|
| "review this PR/code", user submitted code for evaluation | **Review-only** |
| "review and fix", "find and fix issues", you wrote the code | **Review+patch** |
| Ambiguous | **Review-only** — declare it and ask at the end if fixes are wanted |

**Review-only constraints (hard rules, not guidelines):**
- Do NOT call any Edit/Write/file-modification tool during this session.
- If you feel compelled to fix something, add it to [Must Fix] with a suggestion instead.
- Exception: user explicitly upgrades to Review+patch mid-session ("go ahead and fix it") — before making any changes, output: `Mode upgrade: Review-only → Review+patch` and then proceed.

**Review+patch constraints:**
- Complete the full review output first. Do not patch silently.
- Apply only Must Fix items after the review block is complete.
- Suggested Improvements and Confirm Items remain output-only — no unilateral patch.

### Reviewer Role

- You are a **gatekeeper**, not a **rewriter** — point out problems and risks; don't rewrite the author's code *(Review-only mode)*
- You are a **second pair of eyes**, not a **style police** — focus on logic correctness and architecture compliance; leave style to the linter
- You are a **collaborator**, not a **judge** — give specific improvement suggestions, not abstract negations

### Tailoring Review Scope

| Change Scale | Review Depth |
|-------------|-------------|
| < 50 lines, within a single file | Quick review: baseline rules + logic correctness |
| 50–300 lines, cross-file but not cross-module | Standard review: complete workflow |
| > 300 lines, or cross-module / involves public interfaces | Deep review: complete workflow + full architecture compliance check |

---

## Complete Execution Workflow

> **Progress tracking:** At the start of each applicable step, output an updated progress block. For Quick reviews show only Steps 1, 5, 7; for Standard reviews show Steps 1–2, 4–7; for Deep reviews show all steps.
>
> ```
> Code Review Progress
> ✅ Step 1: Understand Change Intent   — <one-line summary, or "in progress">
> ✅ Step 2: Establish Change Context
> ▶  Step 3: Architecture Compliance
> ⬜ Step 4: Code Quality
> ⬜ Step 5: Logic Correctness
> ⬜ Step 6: Impact Scope
> ⬜ Step 7: Review Conclusion
> ```
>
> Replace `⬜` with `▶` for the current step, and `✅` once complete.

---

### Step 1: Understand the Change Intent

Before reviewing any line of code, first clarify three questions:

- What **problem** does this change **aim to solve**? (Requirement/Bug/Optimization/Refactor)
- What is the **expected behavior** after the change?
- **Why was this approach chosen**? (Are there rejected alternative solutions?)

**Information sources:** PR description, commit message, associated issue/ticket, communication with the author.

If the above information is incomplete, **first confirm intent with the author before starting the review**.

### Step 2: Establish Change Context

After understanding the change intent, establish the surrounding context — don't just look at the diff; understand the environment where the diff lives.

**What to understand:**
- What was the modified function/class **originally doing**? How has the behavior changed?
- Which **callers** does the modified code have? Do they depend on the behavior that is about to change?
- Have the **dependencies** of the modified code also been synchronously modified?
- Does the change involve **public interfaces**? If so, is it backward compatible?

🔗 When GitNexus is available, use `context` / `impact` MCP tools to map change context.

### Step 3: Architecture Compliance Review

```
Architecture Compliance Checklist
─────────────────────────────────────────────────────
[ ] Is the layering correct? Any layer-crossing calls in the change?
    (Entry Layer → Logic Layer → Data Layer → Infrastructure Layer, no reversal)
[ ] Has any new circular dependency been introduced?
[ ] Has any existing module's boundary been violated?
    (No direct references to another module's internal implementation)
[ ] Is the dependency direction compliant? Any reverse dependencies?
[ ] Does it follow the Hollywood Principle?
    (Dependencies obtained through injection, not self-constructed/pulled)
[ ] Are shared data structures (DTO / Event) placed in the shared layer?
─────────────────────────────────────────────────────
```

### Step 4: Code Quality Review

**Baseline rules (§0 above — must check regardless of change scale).**

**SOLID principles (add for medium and above changes):**

| Principle | Review Points |
|-----------|--------------|
| SRP | Does the new/modified function do only one thing? Can its responsibility be described in one sentence (without "and")? |
| OCP | Is new behavior added through extension or by modifying existing stable code? |
| LSP | If subclasses are involved, can they transparently replace the base class? Any empty implementations? |
| ISP | If interfaces are involved, are implementors forced to implement unused methods? |
| DIP | Do higher-layer modules directly depend on concrete implementations? Are dependencies obtained through injection? |

**DRY check:** Look for logic blocks appearing 2+ times. Flag cross-file duplication only when function signatures are identical AND the logic body exceeds 10 lines.

### Step 5: Logic Correctness Review

**Review points:**
- **Boundary conditions**: Are null values, zero values, negatives, empty collections, over-long strings, and concurrency scenarios handled?
- **Error paths**: Is the behavior under exceptional conditions as expected? Are error messages meaningful?
- **State consistency**: Is there rollback or compensation when operations fail?
- **Idempotency**: If an operation might be executed multiple times (retry, duplicate consumption), are results consistent?
- **Security**: Any injection risks? Are permission checks in place? Is sensitive data masked?

**Logic review mental framework:**
```
For each branch path in the change, ask three questions:
1. Under what conditions will this branch be entered? (Trigger condition)
2. What happens when it's entered? (Side effects, state changes)
3. If something goes wrong in this branch, what happens? (Error propagation path)
```

### Step 6: Impact Scope Confirmation

```
Impact Completeness Checklist
─────────────────────────────────────────────────────
[ ] Have all callers been adapted to the change? Any missed callers?
[ ] If a public interface was modified, is it backward compatible? If not, is there an explanation?
[ ] Have related type definitions / DTOs / Events been updated synchronously?
[ ] Have related unit tests been updated synchronously? Do they cover new/changed behavior?
[ ] Have related documentation / comments / CHANGELOG been updated synchronously?
[ ] Have related configs / routing / registries been updated synchronously?
─────────────────────────────────────────────────────
```

### Step 7: Output Review Conclusion

```
Review Conclusion
─────────────────────────────────────────────────────
Change summary: <one sentence describing the change content and purpose>
Review result: ✅ Approved / ⚠️ Approved with changes / ❌ Needs redesign

[Must Fix] (must resolve before merge)
  1. <issue description> — <specific location> — <fix suggestion>

[Suggested Improvements] (doesn't block merge, but recommended)
  1. <issue description> — <improvement direction>

[Confirm Items] (questions requiring author confirmation)
  1. <question description>

Impact assessment: <actual impact scope; is it consistent with expectations>
─────────────────────────────────────────────────────
```

**Output discipline:**
- **Classify issues**: Distinguish "must fix" from "suggested improvement"
- **Give specific suggestions**: Don't just say "this is bad" — say "suggest changing to X, because…"
- **Point to the location**: Precise to file name and line range
- **Acknowledge uncertainty**: Put uncertain items in "Confirm Items," don't pretend to be certain

---

## Forbidden Actions

- **Style-first**: Nitpicking personal style preferences on logically correct, architecturally compliant code
- **Vague negation**: "This code feels wrong" but can't identify specific problems
- **Overstepping rewrite (Review-only)**: Providing large blocks of replacement code — the reviewer provides direction
- **Silent patch (Review+patch)**: Fixing issues without first producing the review output — always document findings before patching
- **Context-free review**: Starting line-by-line review without reading PR description or understanding change intent
- **All or nothing**: Rejecting an entire PR because of one minor issue

---

## Common Review Blind Spots

| Blind Spot | Typical Omission | Review Method |
|-----------|-----------------|---------------|
| Indirect callers | Only checked direct callers, missed code that depends indirectly via interfaces/events | Trace event bus and interface implementations |
| Error propagation | Only reviewed the happy path, ignored behavior under exception paths | Review each catch/except block |
| Data races | Only reviewed single-threaded logic, ignored shared state under concurrency | Identify all readers/writers of shared state |
| Backward compatibility | Only reviewed new behavior, ignored whether old callers still work | Check usage patterns of all callers |
| Ghost dependencies | Only reviewed code dependencies, ignored config/env vars/database schema | Check config and external dependencies |
| Duplicate implementation | Newly added code duplicates functionality of existing code | Search for similar implementations |

---

## Reply Format

Review Summary:

| # | Item | Detail |
|---|------|--------|
| [1] | Conclusion | <one sentence: change summary + overall verdict (Approved / Changes needed / Redesign)> |
| [2] | Findings | <Must Fix items + Suggested Improvements, each with location and fix suggestion> |
| [3] | Risks / Assumptions | <impact scope; assumptions about change intent or caller behavior> |
| [4] | Verification | <Steps 3–6 checklist coverage: which checks passed, which were skipped and why> |
| [5] | Needs your input | <Confirm Items — questions requiring author clarification before re-review> |
