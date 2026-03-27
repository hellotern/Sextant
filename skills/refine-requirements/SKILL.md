---
description: >-
  You MUST use this skill before writing any design or code when the requirement is vague, ambiguous, or too broad.
  Use when the "what" is unclear — the requirement needs scoping, feasibility assessment, or decomposition before anyone touches code.
  Stronger signals: "unclear requirements", "break this down", "is this feasible", "help me design", "what do we need to build", vague one-sentence feature requests, open-ended asks like "build me X".
  Skip this skill and go directly to sextant:add-feature only when the requirement is already concrete, scoped, and unambiguous.
---

!../principles/SKILL_BODY.md

!../tool-gitnexus/SKILL_BODY.md

---

# Requirements Analysis and Refinement Workflow

## Core Principle

Requirements are the source of code — when the source is vague, downstream must be chaotic. The goal of requirements refinement is not to produce perfect documentation, but to **eliminate ambiguity, discover contradictions, and complete boundary conditions before writing code**, so that "need to come back and ask" during development approaches zero.

---

## When to Trigger This Workflow

> **Guard:** Enter this workflow when 🔴 red ambiguities exist (gaps that would invalidate or fundamentally redirect implementation), **or** when the user explicitly requests requirements decomposition or feasibility assessment ("break this down", "is this feasible", "help me plan"). If the requirement is clear and no decomposition is requested, skip directly to `sextant:add-feature`.

| Trigger Signal | Description |
|---------------|-------------|
| Feature requirement has 🔴 red ambiguities (undefined scope, conflicting behavior, unclear ownership) | "Support multiple formats" — which formats? async or sync? who calls this? |
| Requirement description has obvious undefined behavior or missing error paths | Success case described but failure case absent |
| User asks to evaluate feasibility before committing to implementation | "Can this be done? How complex is it?" |
| User asks to break down a vague idea into actionable tasks | "Help me break down this requirement" |
| Requirement gaps discovered mid-development that block progress | "This scenario wasn't considered before" |

---

## Complete Execution Workflow

### Step 1: Parse the Original Requirement

Translate the user's natural language requirement into a structured description.

```
Requirement Elements Checklist
─────────────────────────────────────────────────────
Target user: <Who uses this feature?>
Core action: <What operation does the user need to complete?>
Expected result: <What is the system state/output after the operation?>
Trigger condition: <Under what circumstances is this feature triggered?>
Success criteria: <What counts as "done"? Specific verifiable conditions>
─────────────────────────────────────────────────────
```

**If the user's description is only one sentence, first complete the above five elements before continuing.**

**Example:**

> User says: "Add an export feature to the system"

After parsing:
```
Target user: System admin? Regular user? All roles? (→ needs confirmation)
Core action: Export what data? Complete or filtered?
Expected result: What format? CSV? Excel? PDF? (→ needs confirmation)
Trigger condition: Which page to trigger from?
Success criteria: Which fields? Performance requirements for large data volumes?
```

### Step 2: Identify Ambiguities and Gaps

**Eight common requirement gap types:**

| Gap Type | Typical Manifestation | Follow-up Direction |
|----------|----------------------|---------------------|
| **Scope undefined** | "Support multiple formats" | Which specific formats? Priority? How many in the first version? |
| **Boundary undefined** | "Support batch operations" | What's the batch limit? What happens when exceeded? |
| **Error path missing** | Only success scenario described | What happens when the operation fails? What does the user see? |
| **Permissions unclear** | "Users can export" | All users? Or specific roles? |
| **Performance unconstrained** | "Support large data volumes" | How large? Response time requirements? Async needed? |
| **Data source unclear** | "Display user information" | Where does the info come from? Real-time or cached? Which fields? |
| **Interaction details missing** | "Add search feature" | Instant or click-to-search? Fuzzy or exact match? |
| **Backward compatibility not considered** | "Rework old interface" | Can old clients continue to work? Is a transition period needed? |

```
Requirement Gap List
─────────────────────────────────────────────────────
🔴 Must clarify (gap affects architecture/technical solution choices):
  1. <gap description> — <why it matters> — <suggested options>

🟡 Recommended clarification (gap doesn't affect main flow, but affects boundary behavior):
  1. <gap description> — <default assumption> — <impact if assumption is wrong>

🟢 Reasonable default available (can proceed with default; low adjustment cost):
  1. <gap description> — <adopted default value> — <adjustment cost>
─────────────────────────────────────────────────────
```

**Don't throw 20 questions at once.** By priority, resolve 🔴 issues first. 🟡 and 🟢 issues can come with default assumptions for the user to confirm or correct.

### Step 3: Evaluate Feasibility Against Existing Architecture

**Questions to answer:**
- Does the existing architecture already have **similar functionality**? Can it be reused?
- Which **modules need to be modified**? How large is the impact scope?
- Are **new data structures** needed (database tables, DTOs, config items)?
- Does it involve **public interface changes**? Backward compatibility requirements?
- Are there **technical constraints** (performance bottlenecks, third-party API limitations)?

🔗 When GitNexus is available, use `query` / `context` / `impact` MCP tools for architecture feasibility assessment.

```
Architecture Feasibility Assessment
─────────────────────────────────────────────────────
Feasibility conclusion: ✅ Can implement directly / ⚠️ Implementable but with risks / ❌ Requires architecture adjustment

Existing similar functionality: Yes (<name>, can reuse/extend) / No (need to build new)
Modules involved: <list modules that need to be modified/added>
Impact scope: <number of callers involved, cross-module situation>
Technical risks: <performance, compatibility, dependency complexity>
Recommended implementation path: <Extend / New / Refactor>

Prerequisites (must complete before starting development):
  - <e.g., need to create database table first>
─────────────────────────────────────────────────────
```

### Step 4: Break Down into Executable Tasks

**Decomposition principles:**
- **Each task has a clear completion standard** — not "build the export feature," but "implement CSV export including XX fields"
- **Each task can be independently verified** — can be tested alone after completion
- **Tasks sorted by dependency order** — data layer before logic layer, logic layer before entry layer
- **Appropriate task granularity** — too large can't track progress; too small creates management overhead

```
Decomposition Strategy (choose by requirement type)
─────────────────────────────────────────────────────
By layer (for new features):
  Task 1: Data layer — create tables/Models/Repositories
  Task 2: Logic layer — implement Services/Handlers
  Task 3: Entry layer — expose API/UI
  Task 4: Tests — unit tests + integration tests

By scenario (for multi-scenario features):
  Task 1: Core scenario (MVP)
  Task 2: Scenario A extension
  Task 3: Error handling

By risk (for high-uncertainty requirements):
  Task 1: Technical validation (Spike)
  Task 2: Minimum viable version (MVP)
  Task 3: Completion — boundaries, error handling, performance
─────────────────────────────────────────────────────
```

```
Task Breakdown List
─────────────────────────────────────────────────────
Requirement: <one-sentence description>

Task 1: <task title>
  Description: <what to do specifically>
  Completion standard: <what counts as done>
  Dependencies: None / Depends on Task N
  Estimated files involved: <estimate>
─────────────────────────────────────────────────────
```

### Step 5: Form Requirements Confirmation Document

```
Requirements Confirmation Document
═════════════════════════════════════════════════════

Requirement overview: <one sentence>

[Feature Description]
Target user: <who>
Core flow: <user operation steps → system response>
Success criteria: <verifiable conditions>

[Boundaries and Constraints]
Data scope: <supported data volume/formats/types>
Performance requirements: <response time/throughput/concurrency>
Permission control: <which roles can use it>
Backward compatibility: <whether needed/how to handle>

[Error Handling]
Scenario 1: <error condition> → <system behavior>

[Technical Solution Summary]
Implementation path: <extend existing / build new module / refactor>
Modules involved: <list>
Key decisions: <technical choices to be made>

[Task Breakdown]
<Breakdown list from Step 4>

[Items Pending Confirmation]
<Final decisions on 🔴 gaps from Step 2>
<Whether default assumptions for 🟡 gaps are acceptable>

═════════════════════════════════════════════════════
```

**The confirmation document must receive explicit user confirmation before entering the development workflow.**

> For a complete sprint plan with dependency-ordered tasks, skill assignments, and impact radius scores, link `sextant:plan` after the confirmation document is signed off.

---

## Handling Requirement Changes

```
Requirement Change Assessment
─────────────────────────────────────────────────────
Change content: <what changed>
Change reason: <why it needs to change>

Impact analysis:
  Completed work that needs to be reworked: <list>
  Not-yet-started work that needs to be adjusted: <list>
  Newly added work: <list>

Cost assessment:
  Rework cost: <High/Medium/Low>
  Delay risk: <High/Medium/Low>

Recommended options:
  A. Execute the change, accept <rework volume>
  B. Defer to next version
  C. Compromise: <description>
─────────────────────────────────────────────────────
```

---

## Forbidden Actions

- **Accept vague requirements unconditionally**: User says "build an XX" and you directly start writing code
- **Make business decisions for the user**: Technical solutions are yours to suggest; business boundaries are for the user to decide
- **Over-gilding requirements**: User only wants basic functionality but you've designed a complete platform — follow YAGNI
- **Ignore error paths**: Only refine the happy path; avoid discussing "what if it fails"
- **One-time perfect requirements**: Trying to resolve all ambiguity in one conversation — confirm by priority in batches

---

## Reply Format

End every requirements-refinement response with this block (omit a field only if it genuinely has nothing to report):

Requirements Summary:

| # | Item | Detail |
|---|------|--------|
| [1] | Conclusion | <one sentence: requirement name + readiness status (ready / pending clarification)> |
| [2] | Deliverables | <requirements confirmation document produced; task breakdown included; gap list attached> |
| [3] | Risks / Assumptions | <🟡 gaps with default assumptions adopted; unverified technical constraints> |
| [4] | Verification | <all 🔴 gaps resolved? confirmation document ready for sign-off?> |
| [5] | Needs your input | <🔴 gaps still pending answer; 🟡 default assumptions awaiting acceptance> |
