---
name: sextant-tool-gitnexus
description: Use when GitNexus is available in the current project (detected by presence of a .gitnexus/ directory or callable GitNexus MCP tools). Provides enhanced tool-call guidance for all sextant workflows: context, impact, query, trace, diff_review, and rename MCP tools. Invoke alongside the relevant task skill (sextant-fix-bug, sextant-add-feature, etc.) when GitNexus is present.
---

# GitNexus Integration Reference

> Provides full enhanced tool-call guidance for all sextant workflow steps marked 🔗. Use alongside the relevant task skill when GitNexus MCP tools are available.

---

## 1. What is GitNexus

GitNexus indexes a code repository as a **knowledge graph** — calls, dependencies, imports, inheritance, and cross-module relationships become queryable structure. Its MCP tools let the agent answer "who uses this?", "what will this change affect?", and "what looks similar?" without relying only on grep and file-by-file reading.

**Core value comparison:**

| Traditional Approach | GitNexus Approach |
|---------------------|-------------------|
| Grep for function name, read call chain file by file | `context` returns complete caller/callee graph in one call |
| Estimate "what changing here will affect" from experience | `impact` returns layered impact list with confidence scores |
| Use pydeps / madge to detect circular dependencies | `impact both` queries dependency direction directly from the graph |
| Manually search similar implementations | `query` semantic search + cluster membership |
| Manually assess impact after git diff | `diff_review` analyzes actual changed symbols and their graph impact |

---

## 2. MCP Tool Quick Reference

### 2.1 `query` — Semantic Search

**Use for:** finding reference modules, extension points, similar code, config, tests.

```text
query({
  query: string,
  repo?: string
})
```

**Returns:** relevant symbols, file paths, line numbers, symbol types, cluster membership.

### 2.2 `context` — Symbol Context

**Use for:** understanding a symbol's neighborhood: callers, callees, inheritance, execution processes, cluster.

```text
context({
  symbol: string
})
```

**Confidence guide:**
- `>= 0.9`: direct/static relationship
- `0.7 - 0.9`: high-probability inferred relationship
- `< 0.7`: possible relationship; manually confirm if important

### 2.3 `impact` — Impact Analysis

**Use for:** risk analysis before changing code.

```text
impact({
  target: string,
  direction: "upstream" | "downstream" | "both",
  minConfidence?: number
})
```

**Interpretation:**
- Depth 1 = direct dependents / direct dependencies
- Depth 2+ = indirect impact
- Mixed clusters = likely cross-module impact
- Same symbol in both directions = possible cycle

### 2.4 `trace` — Execution Flow Tracing

**Use for:** following a request or business flow from entry point to endpoint.

```text
trace({
  symbol: string
})
```

### 2.5 `diff_review` — Change Impact Review

**Use for:** reviewing already-written code based on the actual git diff.

```text
diff_review()
```

### 2.6 `rename` — Graph-Aware Renaming

**Use for:** safe symbol renaming with graph awareness.

```text
rename({
  symbol: string,
  newName: string
})
```

---

## 3. Tool Selection Guide

```text
Need to understand a symbol?
  -> context

Need to know what will break if it changes?
  -> impact upstream

Need to know what it depends on or check dependency direction?
  -> impact downstream / both

Need to follow an execution path?
  -> trace

Need to find similar implementations / extension points / tests?
  -> query

Need to review the actual diff?
  -> diff_review

Need to rename safely?
  -> rename
```

**Common combinations:**

| Scenario | Call Sequence |
|----------|---------------|
| Bug localization | `query` -> `context` -> `trace` |
| Impact assessment | `impact upstream` -> `impact downstream` |
| Find reference module | `query` -> `context` |
| Architecture audit | `impact both` + `context` + `query` |
| Post-change verification | `diff_review` + `impact upstream` |

---

## 4. Workflow Enhancements

This section mirrors the main workflows. Each subsection is the target of the short `see tool-gitnexus.md` pointers kept in the workflow files.

### 4.1 Add Feature

#### Step 1 — Understand Existing Architecture

**Goal:** find the closest reference module, understand its callers/dependencies, and check for extension points.

```text
query({ query: "<new feature description>" })
context({ symbol: "<core symbol of the best reference module>" })
query({ query: "strategy interface factory registry plugin" })
```

**Use results to answer:**
- what cluster the new feature belongs to
- which module is the best structural reference
- whether a reusable extension point already exists

#### Step 2 — Choose Integration Strategy

**Goal:** decide whether the feature should integrate via registry, abstraction, event bus, config, or invasive modification.

```text
query({ query: "factory register provider plugin" })
query({ query: "abstract interface strategy base class" })
query({ query: "event bus emit subscribe dispatch" })
context({ symbol: "<candidate extension point>" })
```

#### Step 3 — Reference Conventions During Implementation

**Goal:** look up how similar code handles naming, injection, and error handling without browsing the repo manually.

```text
context({ symbol: "<similar function or class in the reference module>" })
```

#### Step 4 — Architecture Compliance Audit

**Goal:** automate the structural parts of the audit.

```text
impact({ target: "<new module core symbol>", direction: "both" })
query({ query: "<new module feature description>" })
context({ symbol: "<new module core symbol>" })
```

**What this verifies well:**
- circular / reverse dependencies
- responsibility overlap
- calls into another module's internals

**Still manual:**
- naming/style consistency
- new side effects/global state
- whether registration/docs/comments must be updated

### 4.2 Bug Fix

#### Step 1 — Reproduce and Locate Root Cause

**Goal:** move from symptom to origin quickly.

```text
query({ query: "<error message keyword or feature description>" })
context({ symbol: "<symbol where the error manifests>" })
trace({ symbol: "<core erroring function>" })
```

**Use results to distinguish:**
- bug exposure location
- likely bug origin location
- full request flow if the chain is long

#### Step 2 — Impact Assessment

**Goal:** quantify caller impact before editing.

```text
impact({ target: "<bug location symbol>", direction: "upstream" })
```

**Use results to fill:**
- caller count
- direct vs indirect impact
- whether the fix crosses clusters/modules

#### Step 4 — Boundary Validation

**Goal:** confirm the fix did not radiate unexpectedly.

```text
impact({ target: "<fixed function>", direction: "upstream" })
diff_review()
```

**Still manual:**
- reproducing the original bug
- running tests
- judging style consistency

### 4.3 Modify Feature

#### Step 1 — Read the Code and Build Context

**Goal:** replace most manual context gathering with one graph query, then fill remaining semantic gaps manually.

```text
context({ symbol: "<target function or class>" })
query({ query: "<event name / callback name / config keyword>" })
query({ query: "<target symbol> test" })
```

**GitNexus covers well:**
- direct callers and dependencies
- related interfaces / inheritance
- process membership
- cluster membership

**Still manual:**
- design intent from comments / PRs / history
- implicit business contracts

#### Step 2 — Impact Analysis

**Goal:** map direct, indirect, and cross-module radiation before changing behavior.

```text
impact({ target: "<change target>", direction: "upstream" })
impact({ target: "<change target>", direction: "downstream" })
diff_review()
```

#### Step 3 — Find Extension Paths

**Goal:** prefer config, extension, or decoration over invasive modification.

```text
query({ query: "<target module> strategy interface factory plugin" })
context({ symbol: "<target function or class>" })
```

#### Step 5 — Signature Change Safety Net

**Goal:** if a public signature changes, generate the caller checklist first.

```text
impact({ target: "<function being modified>", direction: "upstream", minConfidence: 0.8 })
```

#### Step 6 — Compliance Audit

**Goal:** automate the structural checklist.

```text
impact({ target: "<modified symbol>", direction: "both" })
impact({ target: "<modified symbol>", direction: "upstream" })
query({ query: "<shared DTO / Event name>" })
diff_review()
```

**Still manual:**
- whether the diff stayed minimal
- style consistency
- tests
- docs / changelog / convention sync

### 4.4 Requirements Refinement

#### Step 3 — Architecture Feasibility Assessment

**Goal:** decide whether the requirement reuses existing code, extends it, or needs new modules.

```text
query({ query: "<feature keywords from the requirement>" })
context({ symbol: "<most likely affected symbol>" })
impact({ target: "<symbol to be modified>", direction: "upstream" })
query({ query: "strategy interface factory registry plugin" })
```

#### Step 4 — Task Decomposition

**Goal:** use a reference module's layering as a breakdown template.

```text
context({ symbol: "<reference module core class>" })
```

#### Requirement Change Handling

**Goal:** estimate rework when requirements change mid-stream.

```text
impact({ target: "<core symbol involved in the change>", direction: "upstream" })
diff_review()
```

### 4.5 Code Review

#### Step 2 — Establish Change Context

**Goal:** understand the environment around the diff, not just the edited lines.

```text
context({ symbol: "<modified function or class>" })
diff_review()
impact({ target: "<modified symbol>", direction: "upstream" })
```

#### Step 3 — Architecture Compliance Review

**Goal:** automate dependency-direction and boundary checks.

```text
impact({ target: "<new or modified core symbol>", direction: "both" })
context({ symbol: "<new or modified core symbol>" })
```

#### Step 4 — DRY Check

**Goal:** detect likely duplicate implementations.

```text
query({ query: "<functional description of the newly added code>" })
```

#### Step 5 — Error Propagation Trace

**Goal:** inspect where failures travel through the system.

```text
trace({ symbol: "<core function involved in the change>" })
```

#### Step 6 — Impact Completeness

**Goal:** detect unadapted callers and missing synchronized updates.

```text
impact({ target: "<modified function>", direction: "upstream" })
diff_review()
```

### 4.6 Write Tests

#### Step 1 — Analyze the Code Under Test

**Goal:** build a contract profile of the symbol under test.

```text
context({ symbol: "<function or class under test>" })
trace({ symbol: "<function under test>" })
query({ query: "<module under test> test spec" })
```

**Use results to derive:**
- real caller usage patterns
- collaborator/mock candidates
- existing test style and placement

#### Step 2 — Discover Boundary Scenarios

**Goal:** extract realistic scenarios from caller behavior and impact hotspots.

```text
context({ symbol: "<function under test>" })
impact({ target: "<function under test>", direction: "upstream" })
```

#### Step 4 — Identify External Dependencies to Mock

**Goal:** classify collaborators into same-module helpers vs external dependencies.

```text
context({ symbol: "<function under test>" })
```

#### Step 5 — Find Reference Tests

**Goal:** follow existing test structure and style.

```text
query({ query: "<module name under test> test" })
```

---

## 5. When Not to Use GitNexus

- Lightweight tasks where reading the file directly is faster
- Understanding design intent from comments, PRs, or git history
- Inferring business semantics or product meaning
- Replacing actual test execution

---

## 6. Common Misuse

| Misuse | Consequence | Correct Approach |
|--------|-------------|-----------------|
| Trust low-confidence graph edges without checking | False positives or missed dynamic behavior | Manually confirm confidence `< 0.7` when it matters |
| Only look upstream | Miss reverse dependencies | Use `both` for architecture reviews |
| Use `query` where `context` is needed | Get snippets without relationships | Search first, then deep-dive with `context` |
| Forget the index may be stale | Results diverge from current code | Re-run analysis after large structural changes |
| Use `diff_review` without a diff | Empty or misleading result | Ensure there is an actual git diff |

---

## 7. Index Timeliness

GitNexus is a snapshot, not a live parser. Re-index after large refactors, many added files, or when graph output disagrees with the code.

```bash
npx gitnexus analyze
npx gitnexus analyze --force
```

---

## 8. Mapping to Skill Principles

| Skill Principle/Rule | GitNexus Tool | Verification Method |
|---------------------|--------------|---------------------|
| SRP / no layer-crossing calls | `context` | Check whether callees cross layer boundaries |
| OCP / extend rather than modify | `query` | Search for existing extension points |
| DIP / avoid hard-coded construction | `context` | Inspect whether dependencies are pulled directly |
| DRY / avoid duplicate implementations | `query` | Search for similar implementations |
| Dependency direction | `impact both` | Look for reverse dependencies |
| Circular dependency detection | `impact both` | Look for cycles in both directions |
| Module boundary rules | `context` | Ensure callees do not include another module's internals |
