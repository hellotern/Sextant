# Code Review Workflow

> This file is loaded on demand by the `coding-principles` Skill when a code review task is identified. General coding principles (SOLID, DRY, baseline rules, etc.) are in the main SKILL.md and are not repeated here.

---

## Core Principle

The goal of code review is not to find fault, but to **discover design flaws, logic vulnerabilities, and architecture risks before code is merged**. Review quality depends on the reviewer's depth of understanding of the change context — the deeper the understanding, the more fundamental the issues found.

---

## Before You Start

### Reviewer Role

- You are a **gatekeeper**, not a **rewriter** — point out problems and risks; don't rewrite the author's code
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

### Step 1: Understand the Change Intent

Before reviewing any line of code, first clarify three questions:

- What **problem** does this change **aim to solve**? (Requirement/Bug/Optimization/Refactor)
- What is the **expected behavior** after the change? (What should it do after the fix)
- **Why was this approach chosen**? (Are there rejected alternative solutions?)

**Information sources:** PR description, commit message, associated issue/ticket, communication with the author.

If the above information is incomplete, **first confirm intent with the author before starting the review** — reviewing "how" without understanding "why" wastes effort on unimportant details.

### Step 2: Establish Change Context

After understanding the change intent, establish the surrounding context of the changed code — don't just look at the diff; understand the environment where the diff lives.

**What to understand:**
- What was the modified function/class **originally doing**? How has the behavior changed after modification?
- Which **callers** does the modified code have? Do they depend on the behavior that is about to change?
- Have the **dependencies** of the modified code also been synchronously modified?
- Does the change involve **public interfaces**? If so, is it backward compatible?

**🔗 GitNexus Enhanced — Automated context establishment:**

Manually reviewing diff context is prone to missing indirect impacts. GitNexus can establish a complete change view in one go:

```
# 1. For each core symbol involved in the change, get full context
context({ symbol: "<modified function/class name>" })
# Returns: callers, callees, inheritance relationships, execution processes

# 2. If there is already a git diff, directly analyze change impact (most precise)
diff_review()
# Returns: all symbols involved in the change, upstream/downstream impact of each change, whether it's a Breaking Change

# 3. If the change involves multiple files/symbols, check impact one by one
impact({ target: "<modified symbol name>", direction: "upstream" })
# Confirm whether all callers have been handled synchronously
```

**`diff_review` is the most efficient tool in the code review scenario** — it directly analyzes based on actual git diff, without needing to guess which symbols are affected.

### Step 3: Architecture Compliance Review

Use the architecture constraints in SKILL.md (§3) to check each change item for compliance.

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

**🔗 GitNexus Enhanced — Automated architecture checks:**

```
# ① Circular dependency + dependency direction check in one go
impact({ target: "<new/modified core symbol>", direction: "both" })
# Check: downstream should not contain higher-layer modules (reverse dependency signal)
# Check: upstream and downstream should not contain the same symbol (circular dependency signal)

# ② Module boundary check
context({ symbol: "<new/modified core symbol>" })
# Check: callees should not contain private functions/internal implementations of other modules
```

### Step 4: Code Quality Review

Use the baseline rules (§4) and SOLID principles (§1) in SKILL.md to check each item.

**Baseline rules (must check regardless of change scale):**

```
Baseline Rules Checklist
─────────────────────────────────────────────────────
[ ] Exception handling: Any empty catch/except? Are exceptions handled or re-thrown after catching?
[ ] Magic values: Any bare numbers or strings? Are constants named?
[ ] Naming accuracy: Does the function name reflect actual behavior? Any misleading names?
[ ] Parameter validation: Are parameter validity checks at public interface entry points?
[ ] Type declarations: Do public functions have type declarations for parameters and return values?
[ ] Log quality: Do logs include context? Any print("error") style logs?
[ ] Explicit dependencies: Any implicit global state access inside function bodies?
[ ] Side effect isolation: Are I/O and pure computation separated?
─────────────────────────────────────────────────────
```

**SOLID principles (add for medium and above changes):**

| Principle | Review Points |
|-----------|--------------|
| SRP | Does the new/modified function do only one thing? Can its responsibility be described in one sentence (without "and")? |
| OCP | Is new behavior added through extension or by modifying existing stable code? Is there an if/elif chain suitable for extracting a strategy? |
| LSP | If subclasses are involved, can they transparently replace the base class? Any empty implementations? |
| ISP | If interfaces are involved, are implementors forced to implement unused methods? |
| DIP | Do higher-layer modules directly depend on concrete implementations? Are dependencies obtained through injection? |

**DRY check:**

**🔗 GitNexus Enhanced — Detect duplicate code:**

```
# Search for existing implementations with similar functionality to newly added code, check for duplication
query({ query: "<functional description of newly added code>" })
# If a high-similarity existing implementation is returned, flag it as a DRY violation risk
```

### Step 5: Logic Correctness Review

This is the step that most requires human participation — tools can check structure, but logic correctness requires the reviewer to understand business semantics.

**Review points:**

- **Boundary conditions**: Are null values, zero values, negatives, empty collections, over-long strings, and concurrency scenarios handled?
- **Error paths**: Is the behavior under exceptional conditions as expected? Are error messages meaningful?
- **State consistency**: Is there rollback or compensation when operations fail? Could dirty state be left behind?
- **Idempotency**: If an operation might be executed multiple times (retry, duplicate message consumption), are results consistent?
- **Security**: Any injection risks? Are permission checks in place? Is sensitive data masked?

**Logic review mental framework:**
```
For each branch path in the change, ask three questions:
1. Under what conditions will this branch be entered? (Trigger condition)
2. What happens when it's entered? (Side effects, state changes)
3. If something goes wrong in this branch, what happens? (Error propagation path)
```

**🔗 GitNexus Enhanced — Assist in tracking error propagation:**

```
# Trace the complete execution flow of the core function involved in the change, understand where errors will propagate
trace({ symbol: "<core function involved in the change>" })
```

### Step 6: Impact Scope Confirmation

Has the impact of the change been completely covered — any "changed A but forgot to sync B" situations?

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

**🔗 GitNexus Enhanced — Automatically detect omissions:**

```
# List all callers, compare with files actually modified in the diff, find unhandled callers
impact({ target: "<modified function name>", direction: "upstream" })
# If callers returned by impact > files modified in the diff, the difference is potentially missed locations
```

### Step 7: Output Review Conclusion

After the review is complete, output conclusions in the following structure:

```
Review Conclusion
─────────────────────────────────────────────────────
Change summary: <one sentence describing the change content and purpose>
Review result: ✅ Approved / ⚠️ Approved with changes / ❌ Needs redesign

[Must Fix] (must resolve before merge)
  1. <issue description> — <specific location> — <fix suggestion>

[Suggested Improvements] (doesn't block merge, but recommended for future optimization)
  1. <issue description> — <improvement direction>

[Confirm Items] (questions requiring author confirmation)
  1. <question description>

Impact assessment: <actual impact scope of the change, is it consistent with expectations>
─────────────────────────────────────────────────────
```

**Output discipline:**
- **Classify issues**: Distinguish "must fix" from "suggested improvement"; don't treat preferences as defects
- **Give specific suggestions**: Don't just say "this is bad" — say "suggest changing to this, because…"
- **Point to the location**: Precise to file name and line range, making it easy for the author to locate
- **Acknowledge uncertainty**: For "I'm not sure if this is a problem" situations, put them in "Confirm Items," don't pretend to be certain

---

## Forbidden Actions

- **Style-first**: Nitpicking personal style preferences on logically correct, architecturally compliant code (unless it violates baseline rules)
- **Vague negation**: "This code feels wrong" but can't identify specific problems — if uncertain, put it in Confirm Items
- **Overstepping rewrite**: Providing large blocks of replacement code during review — the reviewer provides direction, the implementation belongs to the author
- **Context-free review**: Starting line-by-line review without reading PR description or understanding change intent
- **All or nothing**: Rejecting an entire PR because of one minor issue — handle issues at different levels, small issues can be fixed later

---

## Common Review Blind Spots

| Blind Spot | Typical Omission | Review Method | 🔗 GitNexus Assistance |
|-----------|-----------------|---------------|------------------------|
| Indirect callers | Only checked direct callers, missed code that depends indirectly via interfaces/events | Trace event bus and interface implementations | `impact upstream` covers indirect dependencies |
| Error propagation | Only reviewed the happy path, ignored behavior under exception paths | Review each catch/except block | `trace` to track full execution path |
| Data races | Only reviewed single-threaded logic, ignored shared state under concurrency | Identify all readers/writers of shared state | `impact both` to find shared state consumers |
| Backward compatibility | Only reviewed new behavior, ignored whether old callers still work | Check usage patterns of all callers | `impact upstream` + `context` |
| Ghost dependencies | Only reviewed code dependencies, ignored config/env vars/database schema | Check config and external dependencies | `query` to search config-related code |
| Duplicate implementation | Newly added code duplicates functionality of existing code | Search for similar implementations | `query` semantic search for similar code |

---

## Reply Format

Step 7 produces the primary review output. Structure it around these five fields (Step 7's existing sections map directly):

```
─── Review Summary ──────────────────────────────────────
① Conclusion:         <one sentence: change summary + overall verdict (Approved / Changes needed / Redesign)>
② Findings:           <Must Fix items + Suggested Improvements, each with location and fix suggestion>
③ Risks / Assumptions: <impact scope; assumptions about change intent or caller behavior>
④ Verification:       <Steps 3–6 checklist coverage: which checks passed, which were skipped and why>
⑤ Needs your input:   <Confirm Items — questions requiring author clarification before re-review>
─────────────────────────────────────────────────────────
```
