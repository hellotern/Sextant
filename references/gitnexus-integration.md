# GitNexus Integration Reference

> This file is loaded on demand when GitNexus is detected as available (§0.0). It provides complete MCP tool signatures, return structures, decision guides, and usage pitfalls. The 🔗 markers in workflow files (bugfix / new-module / modify-existing) indicate when to call these tools; this file explains how to call them and how to interpret results.

---

## 1. What is GitNexus

GitNexus indexes a code repository as a **knowledge graph** — every call relationship, dependency chain, import relationship, and inheritance relationship between functions, classes, and modules is parsed and stored in a graph database. It exposes a set of query tools via the MCP protocol, enabling AI agents to obtain **precise structural awareness** before coding, rather than relying on grep guesswork.

**Core value comparison:**

| Traditional Approach | GitNexus Approach |
|---------------------|-------------------|
| Grep for function name, read call chain file by file | `context` returns complete caller/callee graph in one call |
| Estimate from experience "what changing here will affect" | `impact` returns layered impact list with confidence scores |
| Use pydeps / madge to detect circular dependencies | `impact both` queries dependency direction directly from the graph |
| Manually search similar implementations to prevent responsibility overlap | `query` semantic search + cluster membership |
| Manually assess impact after git diff | `diff_review` automatically analyzes change impact based on graph structure |

---

## 2. MCP Tool Signatures and Return Structures

### 2.1 `query` — Semantic Search

**Purpose:** Search the codebase for relevant symbols, files, and code snippets using natural language descriptions. Suitable for "finding things" — finding reference modules, finding extension points, finding similar implementations.

```
query({
  query: string,     // Natural language description, e.g. "payment processing" or "user authentication"
  repo?: string      // Specify when multi-repo; can omit for single repo
})
```

**Key return information:**
- Symbols sorted by relevance, each with file path, line number, symbol type, and cluster membership
- Cluster information reveals the project's functional partitioning — symbols in the same cluster are functionally related
- Semantic search ≠ text matching; can find code with similar functionality but different naming

**Typical scenarios:**
- Find reference before adding a new module: `query({ query: "user authentication login" })`
- Check for responsibility overlap: `query({ query: "<new module feature description>" })`
- Find extension points: `query({ query: "strategy interface factory registry" })`
- Find config-related code: `query({ query: "config environment settings" })`
- Find test files: `query({ query: "<function name> test spec" })`

### 2.2 `context` — Symbol Context

**Purpose:** Get the complete neighborhood graph of a specific symbol (function, class, method). Suitable for "understanding a thing" — who calls it, what it calls, what execution flow it belongs to.

```
context({
  symbol: string    // Symbol name, e.g. "UserService" or "handleLogin"
})
```

**Key return information:**
- **callers**: List of callers (who uses it), each with file path, line number, call type, confidence
- **callees**: List of callees (what it uses)
- **heritage**: Inheritance/implementation relationships (extends / implements)
- **processes**: Execution flows this symbol participates in (complete path from entry to endpoint)
- **cluster**: Functional cluster membership

**Typical scenarios:**
- Bug localization: trace call chain to find root cause
- Reading code: replace manual context building
- Implementation reference: view how a reference module's function is written and where it's located
- Interface discovery: find abstract base classes and all implementations through heritage

**Confidence score interpretation:**
- **≥ 0.9**: Statically determined call relationship (direct function calls, definite imports)
- **0.7 – 0.9**: High-probability calls (type inference, interface implementation)
- **< 0.7**: Possible calls (dynamic dispatch, reflection, string-concatenated calls) — requires manual confirmation

### 2.3 `impact` — Impact Analysis

**Purpose:** Given a change target, analyze the complete impact chain upstream (who depends on it) or downstream (what it depends on). Suitable for "risk assessment" — what will changing this affect.

```
impact({
  target: string,           // Change target symbol name
  direction: "upstream" | "downstream" | "both",
  minConfidence?: number    // Minimum confidence filter; no filter by default
})
```

**Key return information:**
- **Layered structure**: Organized by dependency depth (Depth 1, 2, 3...)
- **Depth 1 (WILL BREAK)**: Direct dependents — necessarily affected after the change
- **Depth 2+ (MAY BREAK)**: Indirect dependents with confidence scores
- **Each item**: Symbol name, file path, line number, call type, confidence, cluster membership

**Direction selection guide:**

| Scenario | Direction | Reason |
|----------|-----------|--------|
| Who will be affected after a bug fix | `upstream` | Query all callers |
| Confirm impact before modifying function signature | `upstream` | Query who uses the old signature |
| Check if new module introduces reverse dependencies | `downstream` | Query what layers the new module depends on |
| Detect circular dependencies | `both` | Query both ways, look for cycles |
| Architecture compliance audit | `both` | Verify direction of both upstream and downstream |

**Determine architecture compliance from `impact` results:**
- **Reverse dependency signal**: `downstream` results contain modules of a higher layer than the target (e.g., Service layer depends on Controller layer)
- **Circular dependency signal**: Same symbol appears in both `upstream` and `downstream`
- **Cross-module signal**: Depth 1 symbols in `upstream` cross different clusters

### 2.4 `trace` — Execution Flow Tracing

**Purpose:** Trace the complete execution flow that a symbol participates in — from entry point to final call. Suitable for understanding "how a request flows."

```
trace({
  symbol: string    // Target symbol name
})
```

**Key return information:**
- All execution flows (processes) this symbol participates in, each flow being an ordered symbol chain from entry to endpoint
- Each node contains symbol name, file path, position in the flow

**Typical scenarios:**
- Bug localization: complete path from entry to error location, quickly pin down which stages data flows through
- Understanding business flow: which Services does an API request pass through from Controller to DB

### 2.5 `diff_review` — Change Impact Review

**Purpose:** Analyze the impact scope of code changes based on actual git diff. More precise than `impact` — because it sees the real changes, not hypothetical ones.

```
diff_review()    // No parameters; automatically reads current git diff
```

**Key return information:**
- All symbols involved in the change
- Upstream/downstream impact of each changed symbol
- Whether the change introduces a Breaking Change
- Suggested locations that need to be updated synchronously

**When to use:**
- **During Step 5 implementation**: After writing some code, check if current changes introduce unexpected impacts
- **During Step 6 review**: Final confirmation of change compliance
- Requires an existing git diff (committed or staged changes)

### 2.6 `rename` — Graph-Aware Renaming

**Purpose:** Not a simple text replacement, but understanding the difference between "function name vs. same-name text in comments vs. variable name" based on the knowledge graph, and only renaming semantically correct references.

```
rename({
  symbol: string,     // Current name
  newName: string     // New name
})
```

**When to use:** When renaming a symbol during refactoring. More reliable than IDE renaming because it understands cross-file call relationships and dynamic references.

---

## 3. Tool Selection Decision Tree

When facing a question that requires understanding code structure, choose tools in the following order:

```
What do I need to understand?
│
├─ "What is this thing? Who uses it? What does it use?"
│   └→ context({ symbol: "..." })
│
├─ "What will be affected if I change this?"
│   └→ impact({ target: "...", direction: "upstream" })
│
├─ "What execution flow does this belong to? How does a request flow?"
│   └→ trace({ symbol: "..." })
│
├─ "Is there something similar in the project? Is there a certain pattern?"
│   └→ query({ query: "..." })
│
├─ "What does the code I changed actually affect?"
│   └→ diff_review()
│
└─ "Need to safely rename a symbol"
    └→ rename({ symbol: "...", newName: "..." })
```

**Common patterns for combined calls:**

| Scenario | Call Sequence | Description |
|----------|--------------|-------------|
| Bug localization | `context` → `trace` | View neighborhood first, then full flow |
| Impact assessment | `impact upstream` → `impact downstream` | Who's affected first, then are dependencies compliant |
| Find reference module | `query` → `context` | Semantic search first, then deep-dive into the most similar result |
| Architecture audit | `impact both` + `query` | Check dependency direction + check responsibility overlap |
| Post-change verification | `diff_review` + `impact upstream` | diff analysis + caller confirmation |

---

## 4. Usage Discipline and Pitfalls

### 4.1 When NOT to Use GitNexus

- **Lightweight tasks** (minor single-function adjustments): Reading code directly is faster than calling tools; don't over-depend
- **Design intent judgment**: GitNexus tells you structure, not "why it was designed this way" — comments, commit messages, PR descriptions still require human reading
- **Business semantics understanding**: Implicit contracts (business meaning of return values, business constraints on call order) require human understanding
- **Test validation**: GitNexus cannot replace running tests; `diff_review` is not equivalent to tests passing

### 4.2 Common Misuse

| Misuse | Consequence | Correct Approach |
|--------|-------------|-----------------|
| Trust all call relationships without checking confidence | Miss dynamic calls, or be confused by false positives | Mark confidence < 0.7 as "requires manual confirmation" |
| Only query upstream without querying downstream | Miss reverse dependency issues | Always use `both` during architecture audits |
| Use `query` instead of `context` | Get relevant code snippets but no call relationships | After finding the target, add `context` to get structure |
| Don't re-analyze after index is stale | Graph data inconsistent with actual code | Re-run `npx gitnexus analyze` after large changes |
| Call `diff_review` without a git diff | No results or error | Ensure there are committed/staged changes |

### 4.3 Index Timeliness

GitNexus's knowledge graph is a **snapshot at index time**, not real-time. Re-indexing is needed in the following situations:

- After large-scale refactoring (file moves, module splits/merges)
- After adding a large number of files
- When `impact` results are inconsistent with actual code

Re-index commands:
```bash
npx gitnexus analyze          # Incremental update (only processes changed files)
npx gitnexus analyze --force  # Force full rebuild
```

---

## 5. Mapping to Coding Principles

The table below summarizes all checkpoints in this Skill that can be enhanced by GitNexus:

| Skill Principle/Rule | Section | GitNexus Tool | Verification Method |
|---------------------|---------|--------------|---------------------|
| SRP — No layer-crossing calls | §1 | `context` | Check if callees cross layers |
| OCP — Extend rather than modify | §1 | `query` | Search for existing strategy interfaces/factories |
| DIP — Dependency injection not hard-coding | §1 | `context` | Check if callees contain direct construction of concrete implementation classes |
| DRY — Same logic exists in only one place | §2 | `query` | Semantic search for similar code snippets |
| Hollywood Principle | §3.1 | `context` | Check constructor's dependency acquisition approach |
| Dependency Direction Rule | §3.2 | `impact both` | Check for reverse paths in bidirectional dependencies |
| Detect Circular Dependencies | §3.2 | `impact both` | Replace pydeps / madge |
| Module Boundary Rules | §3.3 | `context` | callees contain no private symbols from other modules |
