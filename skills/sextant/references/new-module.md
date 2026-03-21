# New Feature / Module Workflow

> This file is loaded on demand by the `coding-principles` Skill when a new feature or module task is identified. General coding principles (SOLID, DRY, baseline rules, etc.) are in the main SKILL.md and are not repeated here.

---

## 🔧 GitNexus Enhanced Mode

> If the current project has already run `npx gitnexus analyze` (i.e., the `.gitnexus/` directory exists), steps marked **🔗 GitNexus** in this workflow should prioritize MCP tool calls over manual reading. When GitNexus is not integrated, ignore all 🔗 markers and follow the original workflow.

---

## Core Principle

When adding new features, **integrate into the existing architecture like a native, not an outsider who starts from scratch**. New code should be fully consistent with existing code in style, structure, and interaction patterns.

---

## Complete Execution Workflow

### Step 1: Understand the Existing Architecture

Before starting, you must be able to answer the following questions:

**Architecture awareness:**
- What architectural pattern does the project use? (MVC / MVVM / Clean Architecture / Component-based / Microservices…)
- How are similar existing features implemented? (Find the best reference)
- What is the logic behind the project's directory structure? (By layer, by feature, by domain?)

**Positioning analysis:**
- Which layer does the new feature belong to? Where is its entry point?
- Which existing modules does the new feature need to depend on?
- Are there already extendable abstraction points (e.g., existing strategy interfaces, factory registries, event buses), or do new ones need to be created?

**Reference module:**
- Find **the most similar existing module** to the new feature as an implementation reference
- Observe its file structure, naming conventions, dependency injection approach, error handling patterns, and test organization
- The new module should follow the same patterns as closely as possible

**🔗 GitNexus Enhanced — Automated architecture understanding:**

Manually reading through the entire project to answer the above questions is slow and prone to missing implicit dependencies. Prioritize the following tools:

```
# 1. Semantic search for the most similar existing module (find reference)
query({ query: "<new feature description, e.g. 'payment processing' or 'user authentication'>" })

# 2. Get full context of the reference module (callers, dependencies, cluster)
context({ symbol: "<core class/function name of the reference module>" })

# 3. Find existing extension points (strategy interfaces, factories, registries)
query({ query: "<strategy pattern OR factory OR registry>" })
```

**Usage strategy:**
- `query` semantic search returns relevant code snippets and cluster membership — this directly answers "how is the project organized"
- The caller/callee relationship graph returned by `context` reveals the reference module's dependency injection approach and inter-module interaction patterns
- If `context` shows the reference module is called through an abstraction interface, the project already has an extension point that can be reused
- Cluster information directly tells you which functional cluster the new feature should belong to

```
Pre-Implementation Research Checklist
─────────────────────────────────────────────
[ ] Understand the project architecture pattern and directory organization (🔗 query cluster info)
[ ] Found the most similar reference module (🔗 query semantic search)
[ ] Determined which layer the new feature belongs to (🔗 context layering relationship)
[ ] Determined the new feature's dependencies (🔗 context dependency graph)
[ ] Confirmed whether there are extendable abstraction points (🔗 query for interfaces/factories)
[ ] Confirmed no overlap with responsibilities of existing modules (🔗 query for similar features)
─────────────────────────────────────────────
```

### Step 2: Design the Solution

Before writing code, clarify the design:

**Location decision:**
- Place it at the same directory level as similar features
- If it's an entirely new domain, create a parallel structure referencing existing module directory structure

**Integration approach (priority order, high to low):**
```
Integration Strategy Priority
─────────────────────────────────────────────
1. Registry-based: Register with existing factory/registry/routing table → zero changes to existing code
2. Extension-point-based: Implement existing abstraction/strategy interface → add only, don't modify
3. Event-driven: Publish/subscribe via event bus → decoupled from existing modules
4. Config-driven: Enable new feature through config files → main flow is unaware
5. Invasive: Modify existing module code to integrate new feature → last resort
─────────────────────────────────────────────
```

**🔗 GitNexus Enhanced — Assist in choosing integration strategy:**

```
# Find existing factory/registry patterns (determine if strategy 1 is applicable)
query({ query: "factory register provider plugin" })

# Find existing abstraction/strategy interfaces (determine if strategy 2 is applicable)
query({ query: "abstract interface strategy base class" })

# Find event bus/pub-sub (determine if strategy 3 is applicable)
query({ query: "event bus emit subscribe dispatch" })
```

If any of the above searches have hits, get the full context of that extension point:
```
context({ symbol: "<name of the hit factory/interface/event bus>" })
```

This will reveal: which existing modules are integrated through this extension point (as implementation examples for the new module), and what the interface contract of this extension point is.

**For large tasks, inform the user of:**
- Which integration approach is being used
- The responsibility boundary of the new module
- How it interacts with existing modules
- Expected file structure

Confirm before implementing.

### Step 3: Implement — Follow Architecture Conventions

> ⚠️ **All principles in SKILL.md (SOLID, DRY, baseline rules, etc.) apply to every line of code written in this step — satisfy them as you write, not as an afterthought.**

**Naming:** Fully consistent with the project's existing naming style (camelCase/snake_case, prefix/suffix conventions, abbreviation habits)

**Dependency direction:** Only upper layers depend on lower layers; reverse dependencies are not allowed. New modules must not introduce reverse dependencies.

**Interface protocol:** Interaction with existing modules must be consistent — if existing modules communicate through dependency injection, the new module uses dependency injection; if through event bus, use event bus.

**Extend, don't modify:** Prioritize OCP-compatible integration; avoid changing existing stable modules.

**Internal module structure:**
- Internal classes/functions are private by default; only expose necessary public interfaces
- Public interfaces must have explicit type declarations and parameter validation
- If the module needs to share data structures with other modules, place them in a dedicated shared layer

**Hollywood Principle:** New modules only declare dependencies (constructor injection / config registration) and do not proactively pull them.

```python
# ✅ Correct dependency approach for new module
class NewFeatureService:
    def __init__(self, repo: FeatureRepository, bus: EventBus):
        self._repo = repo
        self._bus = bus

# ❌ Incorrect dependency approach for new module
class NewFeatureService:
    def __init__(self):
        self._repo = MySQLFeatureRepository("localhost")  # Self-construct
        self._bus = EventBus.get_instance()                # Proactively pull
```

**🔗 GitNexus Enhanced — Real-time reference during implementation:**

While writing code, if you're unsure about a convention (naming, error handling, dependency injection), use `context` at any time to see how the reference module handles the equivalent function:

```
# See how the reference module handles errors in a similar function
context({ symbol: "<similar function name in reference module>" })
```

This is faster than browsing files and shows the function's position in the entire call chain, helping understand why it's written that way.

### Step 4: Architecture Compliance Audit (Required)

After completing the new module, run through an architecture audit:

```
New Module Architecture Audit Checklist
─────────────────────────────────────────────────────
[ ] Is the layering correct? No layer-crossing calls?
[ ] Has any circular dependency been introduced?
[ ] Has any existing module's boundary been violated? (No direct references to other modules' internal implementations)
[ ] Does the new module's responsibility overlap with existing modules?
[ ] Is the external interface consistent with project style? (Naming, parameter style, error handling)
[ ] Has any new global state or side effects been introduced?
[ ] Is the dependency direction compliant? Any reverse dependencies?
[ ] Does it follow the Hollywood Principle? (Dependencies injected, not pulled)
[ ] Does documentation / comments / type definitions / routing config need to be updated?
[ ] Does it need to be registered with existing factories / registries / config files?
─────────────────────────────────────────────────────
```

**🔗 GitNexus Enhanced — Automated audit checklist:**

The following checklist items can be verified through GitNexus tool calls, no longer relying on manual reading:

```
# ① "Has circular dependency been introduced" + "Is dependency direction compliant"
# Query the new module's bidirectional dependencies, check for reverse or circular dependencies
impact({ target: "<new module core class name>", direction: "both" })
# Check: downstream should not contain higher-layer modules; upstream should not contain lower-layer modules

# ② "Does the new module's responsibility overlap with existing modules"
# Semantic search for similar functionality, confirm no duplicate implementation
query({ query: "<new module's core feature description>" })
# Check: if results contain high-similarity existing implementations, there may be responsibility overlap

# ③ "Has any existing module's boundary been violated"
# Query the new module's dependencies, confirm only public interfaces are used
context({ symbol: "<new module core class name>" })
# Check: callees list should not contain private functions/internal implementations of other modules
```

The following checklist items still require manual review (GitNexus cannot determine):
- Whether the external interface is consistent with project style (naming, parameter style is subjective)
- Whether new global state or side effects have been introduced (requires reading code logic)
- Whether the Hollywood Principle is followed (requires inspecting constructor implementation)
- Whether documentation needs updating / registration with factory (requires knowledge of project conventions)

Audit results must be clearly communicated to the user: **Passed ✅** or **Issues found ⚠️ (with specific details)**.

---

## Common Pitfalls

| Pitfall | Description | Correct Approach | 🔗 GitNexus Detection |
|---------|-------------|-----------------|----------------------|
| Responsibility overlap | New module implements functionality already covered by existing modules | Search for existing implementations first; prefer reusing or extending | `query` semantic search for similar features |
| Style break | New code is inconsistent with existing project style (naming, indentation, comment language) | Strictly reference the most similar existing module | `context` to see reference module approach |
| Over-abstraction | New module only has one implementation yet introduces an abstraction layer | Follow YAGNI; abstract only when there's a second implementation | — |
| Implicit coupling | New module interacts with other modules through global variables or implicit conventions | All interactions through public interfaces or event bus | `impact both` to check dependency paths |
| Missing registration | New module implemented but forgot to register with factory/routing/config | Audit checklist includes registration check | `query` to search registry for confirmation |
| Reverse dependency | For "convenience," lower-layer module references higher-layer module | Strictly follow dependency direction rules | `impact downstream` to verify |
