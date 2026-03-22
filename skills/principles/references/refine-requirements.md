# Requirements Analysis and Refinement Workflow

> This file is loaded on demand by the `coding-principles` Skill when a requirements analysis, refinement, or review task is identified. General coding principles (SOLID, DRY, baseline rules, etc.) are in the main SKILL.md and are not repeated here.

---

## 🔧 GitNexus Enhanced Mode

> If the current project has already run `npx gitnexus analyze` (i.e., the `.gitnexus/` directory exists), steps marked **🔗 GitNexus** in this workflow should prioritize MCP tool calls over manual reading. When GitNexus is not integrated, ignore all 🔗 markers and follow the original workflow.

---

## Core Principle

Requirements are the source of code — when the source is vague, downstream must be chaotic. The goal of requirements refinement is not to produce perfect documentation, but to **eliminate ambiguity, discover contradictions, and complete boundary conditions before writing code**, so that "need to come back and ask" during development approaches zero.

---

## When to Trigger This Workflow

| Trigger Signal | Description |
|---------------|-------------|
| User provides a feature requirement in natural language | "I want to build an XXX" |
| Requirement description has obvious ambiguity or undefined behavior | "Support multiple formats" — which formats? |
| User asks to evaluate feasibility of a requirement | "Can this be done? How?" |
| User asks to break down a vague idea into actionable development tasks | "Help me break down this requirement" |
| Requirement gaps discovered during development that need to be revisited | "This scenario wasn't considered before" |

---

## Complete Execution Workflow

### Step 1: Parse the Original Requirement

Translate the user's natural language requirement into a structured description.

**Extract the following elements:**

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

**If the user's description is only one sentence, first complete the above five elements before continuing.** Don't start analysis with incomplete elements — vague input only produces vague output.

**Example:**

> User says: "Add an export feature to the system"

After parsing:
```
Target user: System admin? Regular user? All roles? (→ needs confirmation)
Core action: Export what data? Complete or filtered?
Expected result: What format is the export file? CSV? Excel? PDF? (→ needs confirmation)
Trigger condition: Which page to trigger from? Button location?
Success criteria: Which fields does the export file contain? Performance requirements for large data volumes?
```

### Step 2: Identify Ambiguities and Gaps

Review each element from Step 1 one by one, marking all undefined or multi-interpretable items.

**Eight common requirement gap types:**

| Gap Type | Typical Manifestation | Follow-up Direction |
|----------|----------------------|---------------------|
| **Scope undefined** | "Support multiple formats" | Which specific formats? Priority? How many in the first version? |
| **Boundary undefined** | "Support batch operations" | What's the batch limit? What happens when exceeded? |
| **Error path missing** | Only success scenario described | What happens when the operation fails? What does the user see? |
| **Permissions unclear** | "Users can export" | All users? Or specific roles? |
| **Performance unconstrained** | "Support large data volumes" | How large is large? Response time requirements? Async needed? |
| **Data source unclear** | "Display user information" | Where does the info come from? Real-time query or cached? Which fields? |
| **Interaction details missing** | "Add search feature" | Instant search or click-to-search? Fuzzy or exact match? |
| **Backward compatibility not considered** | "Rework old interface" | Can old clients continue to work? Is a transition period needed? |

**Output format:**

```
Requirement Gap List
─────────────────────────────────────────────────────
🔴 Must clarify (gap affects architecture/technical solution choices):
  1. <gap description> — <why it matters> — <suggested options>
  2. ...

🟡 Recommended clarification (gap doesn't affect main flow, but affects boundary behavior):
  1. <gap description> — <default assumption> — <impact if assumption is wrong>
  2. ...

🟢 Reasonable default available (can proceed with default; low adjustment cost):
  1. <gap description> — <adopted default value> — <adjustment cost>
─────────────────────────────────────────────────────
```

**Classification discipline:**
- 🔴 Red gaps: Development cannot begin without clarification, or different interpretations lead to completely different technical solutions
- 🟡 Yellow gaps: Can proceed with assumptions, but incorrect assumptions require rework
- 🟢 Green gaps: Reasonable default value available; low adjustment cost

**Don't throw 20 questions at once.** By priority, resolve 🔴 issues first. 🟡 and 🟢 issues can come with default assumptions for the user to confirm or correct.

### Step 3: Evaluate Feasibility Against Existing Architecture

Requirements don't exist in a vacuum — they need to land in an existing code architecture. This step checks whether the requirements are feasible under the current architecture and what the most natural implementation path is.

**Questions to answer:**
- Does the existing architecture already have **similar functionality**? Can it be reused or does new code need to be built?
- Which **modules need to be modified** for the requirements to land? How large is the impact scope?
- Are **new data structures** needed (database tables, DTOs, config items)?
- Does it involve **public interface changes**? Are there backward compatibility requirements?
- Are there **technical constraints** (performance bottlenecks, third-party API limitations, concurrency issues)?

**🔗 GitNexus Enhanced — Quick architecture feasibility assessment:**

```
# 1. Search for existing similar functionality (determine reuse vs. new build)
query({ query: "<feature keywords from requirement description>" })
# If high-similarity results found → prioritize evaluating the option to extend existing implementation
# If no similar results → need to build a new module; reference add-feature.md workflow

# 2. Assess the modules involved and impact scope of the requirement
context({ symbol: "<core class/function most likely to be modified by the requirement>" })
# Determine the radiation range of the change from callers and callees

# 3. If the requirement involves modifying existing functionality, assess change impact
impact({ target: "<function/class to be modified>", direction: "upstream" })
# Number of Depth 1 callers and cross-cluster situation directly reflects implementation risk

# 4. Search for existing extension points (strategy interfaces, factories, registries)
query({ query: "strategy interface factory registry plugin" })
# If the requirement can be implemented by registering a new strategy, it's much lower risk than invasive modification
```

**Output format:**

```
Architecture Feasibility Assessment
─────────────────────────────────────────────────────
Feasibility conclusion: ✅ Can implement directly / ⚠️ Implementable but with risks / ❌ Requires architecture adjustment

Existing similar functionality: Yes (<name>, can reuse/extend) / No (need to build new)
Modules involved: <list modules that need to be modified/added>
Impact scope: <number of callers involved, cross-module situation> (🔗 impact results)
Technical risks: <performance, compatibility, dependency complexity>
Recommended implementation path: <Extend / New / Refactor>

Prerequisites (must complete before starting development):
  - <e.g., need to create database table first>
  - <e.g., need to confirm API capabilities with third party first>
─────────────────────────────────────────────────────
```

### Step 4: Break Down into Executable Tasks

Break down the refined requirements into independent, deliverable development tasks.

**Decomposition principles:**
- **Each task has a clear completion standard** — not "build the export feature," but "implement CSV export including XX fields, supporting XX number of records"
- **Each task can be independently verified** — can be tested alone after completion; doesn't depend on other tasks finishing first
- **Tasks sorted by dependency order** — dependencies first (data layer before logic layer, logic layer before entry layer)
- **Appropriate task granularity** — too large ("build the entire module") can't track progress; too small ("add one constant") creates management overhead

**Decomposition patterns:**

```
Decomposition Strategy (choose by requirement type)
─────────────────────────────────────────────────────
By layer: Suitable for new features
  Task 1: Data layer — create tables/Models/Repositories
  Task 2: Logic layer — implement Services/Handlers
  Task 3: Entry layer — expose API/UI
  Task 4: Tests — unit tests + integration tests

By scenario: Suitable for multi-scenario features
  Task 1: Core scenario (MVP)
  Task 2: Scenario A extension
  Task 3: Scenario B extension
  Task 4: Boundary/error handling

By risk: Suitable for high-uncertainty requirements
  Task 1: Technical validation (Spike) — validate key technical assumptions
  Task 2: Minimum viable version (MVP) — validate business assumptions
  Task 3: Completion — fill in boundaries, error handling, performance optimization
─────────────────────────────────────────────────────
```

**🔗 GitNexus Enhanced — Assist in layer-based decomposition:**

```
# View the layering structure of the reference module as a decomposition reference
context({ symbol: "<reference module core class>" })
# From the layering relationships in callees, see: what layer components make up this module
# New module task decomposition can reference the same layer structure
```

**Task output template:**

```
Task Breakdown List
─────────────────────────────────────────────────────
Requirement: <one-sentence description>

Task 1: <task title>
  Description: <what to do specifically>
  Completion standard: <what counts as done>
  Dependencies: None / Depends on Task N
  Estimated files involved: <estimate>
  Estimated time: <estimate>

Task 2: ...
─────────────────────────────────────────────────────
```

### Step 5: Form Requirements Confirmation Document

Consolidate all the above analysis into a requirements confirmation document, get user confirmation before starting development.

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
Scenario 2: <error condition> → <system behavior>

[Technical Solution Summary]
Implementation path: <extend existing / build new module / refactor>
Modules involved: <list>
Key decisions: <technical choices to be made>

[Task Breakdown]
<Breakdown list from Step 4>

[Items Pending Confirmation]
<Final decisions on 🔴 gaps from Step 2>
<Whether default assumptions for 🟡 gaps from Step 2 are acceptable>

═════════════════════════════════════════════════════
```

**The confirmation document must receive explicit user confirmation before entering the development workflow.**

---

## Handling Requirement Changes

Requirement changes during development are normal. The key is not to prevent changes, but to **evaluate the cost of the change and let the user make an informed decision**.

**Change evaluation template:**

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

**🔗 GitNexus Enhanced — Quickly assess change impact:**

```
# Assess impact scope of existing code involved in the requirement change
impact({ target: "<core symbol involved in the change>", direction: "upstream" })
# Number of callers and cluster distribution directly reflects rework scope

# If there's already partial implementation, use diff_review to assess impact of completed work
diff_review()
```

---

## Forbidden Actions

- **Accept vague requirements unconditionally**: User says "build an XX" and you directly start writing code — must first complete the elements
- **Make business decisions for the user**: Technical solutions are yours to suggest; business boundaries are for the user to decide — "which formats to support" is not a technical question
- **Over-gilding requirements**: User only wants basic functionality but you've designed a complete platform — follow YAGNI
- **Ignore error paths**: Only refine the happy path; avoid discussing "what if it fails"
- **One-time perfect requirements**: Trying to resolve all ambiguity in a single conversation — confirm by priority in batches; resolve 🔴 issues first

---

## Common Pitfalls

| Pitfall | Manifestation | Correct Approach | 🔗 GitNexus Assistance |
|---------|--------------|-----------------|------------------------|
| Solution first | Started discussing technical solutions before understanding requirements | Complete Steps 1–2 first, then go to Step 3 | — |
| Scope creep | "Add XX while we're at it" keeps piling on | Run change assessment for every addition | `impact` to assess impact of added feature |
| Architecture unknown | Breaking down tasks without knowing existing architecture | Step 3 architecture feasibility assessment is mandatory | `query` + `context` to build architecture understanding |
| Missing permissions | Only considered functional logic, ignored "who can use it" | Eight gap types must include permission item | — |
| Ignoring existing code | Requirements involve modifying existing functionality but impact not assessed | Existing code involvement must have impact analysis | `impact upstream` to assess radiation scope |
| Wrong granularity | Task decomposition either too coarse or too fine | Each task has clear completion standard and can be independently verified | — |
