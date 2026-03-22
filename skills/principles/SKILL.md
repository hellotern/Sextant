---
name: sextant
description: General coding core principles. Use this Skill as the default coding guideline when the user requests code implementation, bug fixes, refactoring, code review, writing test cases, or requirements analysis and refinement, and no more specific technical Skill matches. Not applicable to lightweight scenarios such as one-off scripts, demos/prototypes, algorithm problems, or notebooks (unless the user explicitly requests adherence to standards).
---

# General Coding Principles

> **Core Goal: Make code easy to read, modify, and extend.** When principles conflict, the final arbitration standard is "lowest long-term maintenance cost for the team." Standards are tools, not chains.

---

## §0 — Task Identification and Rule Activation

### 0.0 Environment Detection and Tool Enhancement

Before starting any coding task, **first check whether the current project has GitNexus integrated**:

**Detection method:** Check whether a `.gitnexus/` directory exists in the project root, or whether the current environment can call GitNexus MCP tools (such as `context`, `impact`, `query`).

**Detection result:**
- **GitNexus available** → Read `references/tool-gitnexus.md` and activate enhanced mode. In subsequent steps, all steps marked 🔗 should prioritize MCP tool calls over manual reading and grep searches.
- **GitNexus unavailable** → Ignore all 🔗 markers and follow the original workflow. No existing workflow is affected.

> GitNexus is an accelerator, not a prerequisite. All workflows work fully without GitNexus; with GitNexus, efficiency and precision are higher.

### 0.1 Identify Task Type and Load Corresponding Workflow

After identifying the specific task type, **first read the corresponding reference file**, then begin execution:

| Task Type | Load File |
|-----------|-----------|
| Bug Fix | → Read `references/fix-bug.md` |
| New Feature / New Module | → Read `references/add-feature.md` |
| Modify / Enhance / Refactor Existing Feature | → Read `references/modify-feature.md` |
| Code Review | → Read `references/review-code.md` |
| Write Test Cases / Add Tests | → Read `references/write-tests.md` |
| Requirements Analysis / Refinement / Review | → Read `references/refine-requirements.md` |
| General Coding (none of the above) | → Use only the general principles in this file |
| *(§0.0 detects GitNexus available)* | → Additionally read `references/tool-gitnexus.md` |

### 0.2 Assess Task Scale and Activate Rules Accordingly

The rules in this Skill are **not executed in full every time**, but are activated in tiers based on task scale:

**Lightweight tasks** (adjustments within a single function, config changes, style fixes, utility function writing)
Activate only the baseline rules (§4): style consistency, minimal changes, no swallowed exceptions, accurate naming.

**Medium tasks** (add functions/classes, modify module internal logic, bug fixes)
Additionally activate: SRP, DRY, interface contracts (parameter validation, return type), read all direct callers to confirm no breakage.

**Large tasks** (cross-module changes, public interface modifications, new modules, architecture adjustments)
Full activation: complete SOLID review, impact analysis, confirm plan before implementation, architecture compliance audit.

**Assessment tips:** Watch for two signals — (1) Does the change cross file boundaries? (2) Does it involve public interface / shared data structure changes? If either is yes, treat it as at least "medium."

### 0.3 Exempt Scenarios and Early Exit

The following scenarios can relax or even skip most rules, **retaining only the baseline rules** (§4):
- One-off scripts / temporary tools
- Demos / prototypes / POCs
- Algorithm problems / competitive programming
- Notebooks / data exploration
- User explicitly asks for "code first, architecture discussion later"
- User explicitly asks for minimal implementation / quick delivery

**Mid-process early exit:** If the user interrupts at any workflow step with phrases like "just write it", "skip the analysis", "just do it", or "stop explaining and implement" — immediately jump to the implementation step and apply only the baseline rules (§4). Do not insist on completing earlier steps. Briefly acknowledge the shortcut (e.g., "Skipping analysis, implementing directly.") and proceed.

---

## §1 — SOLID Principles

### SRP — Single Responsibility

Each module, class, and function does **one thing** and has **one reason to change**.

**Assessment tip:** Describe the responsibility in one sentence. If "and," "as well as," or "also" appears, it usually needs to be split.

**Layered responsibilities (adapt flexibly to project architecture; no layer-crossing allowed):**
```
Entry Layer (Controller / Router / View)    → Input validation, routing, response
Logic Layer (Service / ViewModel / Handler) → Business logic orchestration
Data Layer (Repository / Store / DAO)       → Data read/write, no business logic
Model Layer (Model / Entity / Schema)       → Data structure definitions
Utility Layer (Util / Helper / Lib)         → Stateless utility functions
```

If a function is obviously too long, consider splitting it first (rule of thumb: ~30 lines, not a hard limit).

**❌ Violation examples:**
```python
# Logic layer directly accesses database — layer violation
def get_user(user_id):
    return db.execute("SELECT * FROM users WHERE id = ?", user_id)

# Entry layer contains business logic — layer violation
def create_order(request):
    if request.amount > user.balance:
        raise Exception("Insufficient balance")
```

### OCP — Open-Closed Principle

Open for extension, closed for modification. New behavior is preferably added through extension rather than modifying existing stable code.

**Recognition signals:** Large `if/elif/switch` dispatching by type; requirements say "currently supports A, will need B and C later"; multiple classes with similar structure but different behavior.

**✅ Strategy pattern isolates the axis of change:**
```python
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool: ...

class OrderService:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy

    def checkout(self, amount: float):
        return self._strategy.pay(amount)
        # Add new payment method: just add a strategy class, OrderService stays unchanged
```

**❌ Violation example:**
```python
def checkout(amount, method):
    if method == "alipay": ...
    elif method == "wechat": ...
    elif method == "stripe": ...   # New requirement → modified old code
```

### LSP — Liskov Substitution

Subclasses must be transparently substitutable for their base classes without changing program correctness.

- Subclasses must not narrow preconditions, widen postconditions, or throw exceptions outside the contract
- If a subclass needs to leave a method empty, the inheritance relationship is wrong; consider composition or redesigning the abstraction

### ISP — Interface Segregation

Keep interfaces small; do not force implementors to depend on methods they don't need. If an implementing class can only provide an empty implementation or throw an exception for some method, the interface is too fat and needs to be split.

### DIP — Dependency Inversion

High-level modules do not depend on low-level implementations; both depend on abstractions. Modules receive dependencies through constructor injection or configuration registration, rather than instantiating concrete implementations themselves.

```python
# ✅ Inject abstraction
class UserService:
    def __init__(self, repo: UserRepository):  # UserRepository is an abstraction
        self._repo = repo

# ❌ Hard-coded dependency
class UserService:
    def __init__(self):
        self._repo = MySQLUserRepository()  # Directly depends on concrete implementation
```

---

## §2 — DRY, YAGNI, and Design Patterns

### DRY — Same Logic Exists in Only One Place

- If the same logic appears 2+ times, extract it into a shared function/component
- Constants must not be hardcoded in multiple places; define them centrally
- Copy-paste with minor tweaks is forbidden; abstract with parameters instead

**Refactoring signals:**

| Code Symptom | Recommended Direction |
|-------------|----------------------|
| Similar if/else dispatching by type in multiple places | Strategy Pattern / Registry Map |
| Multiple functions with the same pre/post processing | Decorator / Middleware / AOP |
| Same data structure assembled in multiple places | Builder Pattern |
| Multiple subclasses repeating the same algorithm skeleton | Template Method Pattern |
| Multiple places subscribing to the same state change | Observer Pattern / Event Bus |

### YAGNI — Code Only for Current Requirements

Do not write code in advance for "might be needed in the future" scenarios. Introduce abstraction only when there is a clear second use case. **Decision standard:** "Does this abstraction have two different concrete implementations right now?" If not, don't abstract yet.

### Design Pattern Decision Rules

> Only introduce design patterns when there is a clear axis of change, repeated branching, or complex object construction; otherwise prefer direct implementation. Over-engineering is more dangerous than under-engineering.

| Problem Scenario | Recommended Pattern | Core Value |
|-----------------|---------------------|------------|
| Control a class to have only one instance | Singleton | Resource control (Note: misuse = global variable) |
| Object type determined at runtime | Factory / Abstract Factory | Decouple creation from usage |
| Same algorithm with multiple implementations, switch at runtime | Strategy | Eliminate if/else; extend without modifying old code |
| Fixed algorithm skeleton with customizable steps | Template Method | Reuse skeleton, open customization points |
| State changes need to notify multiple dependents | Observer / Event Bus | Decouple publisher from subscriber |
| Dynamically add responsibilities | Decorator | Don't modify original class; flexible composition |
| Unified entry to complex subsystems | Facade | Simplify external calls |
| Constructor parameter explosion (>4) | Builder | Chain construction, clear semantics |
| Encapsulate requests as objects (undo/queue) | Command | Decouple operations, support undo/redo |
| Coordinate multiple objects, avoid cross-referencing | Mediator | Mesh dependency → Star dependency |

---

## §2.5 — Conflict Arbitration

The opening rule says "lowest long-term maintenance cost" is the final arbiter. The following examples translate that into concrete verdicts for the most common principle collisions.

### DRY vs YAGNI — Shared logic with only one caller

**Scenario:** Two functions share 80% of their logic, but each has exactly one caller and serves a distinct context.

**Verdict: YAGNI wins.** Do not extract the shared logic yet.

**Reasoning:** Shared code creates coupling. If the two contexts evolve in different directions, a single shared function either accumulates conditional parameters or gets forked anyway. Wait until a third caller appears, or until the duplication demonstrably causes a maintenance problem (e.g., a bug that must be fixed in two places), before abstracting.

**Signal to flip:** The duplicated block is non-trivial (>10 lines), contains a bug that must be fixed in both copies, or a product requirement explicitly introduces a third consumer.

### OCP vs YAGNI — Abstraction with no second implementation

**Scenario:** A class has exactly one concrete implementation. Strictly following OCP would mean wrapping it in an interface "just in case" a second implementation is needed later.

**Verdict: YAGNI wins.** Ship the concrete class directly without an abstraction layer.

**Reasoning:** Premature interfaces increase cognitive overhead and indirection for every future reader. OCP responds to *known* axes of variation, not speculative ones. Adding an interface later — when the second implementation actually exists — is cheap; maintaining an unnecessary abstraction forever is not.

**Signal to flip:** The requirement doc explicitly says "support pluggable X," or the code is part of a library/SDK where external teams will supply their own implementations.

### DRY vs Layer Boundaries — Shared logic that crosses layers

**Scenario:** The same validation or transformation logic appears in both the entry layer and the logic layer. Extracting it into a shared utility would satisfy DRY, but the utility would need to import types from both layers, violating the dependency direction rule.

**Verdict: Layer boundary wins.** Tolerate the duplication. Keep the logic in each layer independently.

**Reasoning:** Architectural integrity ranks above DRY because cross-layer coupling destabilizes the entire dependency graph. A layer boundary violation affects every module on both sides; local duplication affects only two files. Duplication is fixable by moving code; a layer violation requires restructuring the entire graph.

**Signal to flip:** If the shared logic is substantial and stable (e.g., a domain value object), introduce a proper shared layer (e.g., `domain/` or `common/`) that neither business layer owns, and have both depend on it downward — this resolves both DRY and the layer constraint simultaneously.

---

## §3 — Architecture Constraints (Always Active)

### 3.1 Hollywood Principle

**"Don't call us, we'll call you."** Modules only declare dependencies (constructor injection / config registration) and do not proactively pull them.

```python
# ✅ Declare dependencies, injected from outside
class EmotionEngine:
    def __init__(self, memory: MemoryStore, event_bus: EventBus, config: EmotionConfig):
        self._memory = memory
        self._bus = event_bus
        self._config = config

# ❌ Self-construct/pull dependencies
class EmotionEngine:
    def __init__(self):
        self._memory = RedisMemoryStore("localhost:6379")
        self._bus = EventBus.get_instance()
        self._config = yaml.load(open("config.yaml"))
```

### 3.2 Dependency Direction Rules

```
Allowed dependency directions (one-way, must not be reversed):
─────────────────────────────────────────────────────────────
Entry Layer  →  Logic Layer  →  Data Layer  →  Infrastructure Layer

Utility Layer ← Any layer can depend on it,
                but Utility Layer must not depend on business layers
─────────────────────────────────────────────────────────────
```

**Forbidden:** Upward dependencies, circular dependencies, infrastructure layer being aware of business concepts.

**Detect circular dependencies:** Use `pydeps` for Python; `madge` for TS/JS. 🔗 When GitNexus is available, `impact({ target: "<module>", direction: "both" })` can directly detect circular and reverse dependencies from the knowledge graph, covering all languages without additional tools.

### 3.3 Module Boundary Rules

- Cross-module communication goes through public interfaces or event buses; direct references to another module's internal implementation are forbidden
- Module internals are private by default; only explicitly marked items are exposed publicly
- Shared data structures (DTO / Event Payload) belong to a dedicated shared layer, not to any single business module

---

## §4 — Code Quality Baselines (Non-Negotiable in Any Scenario)

The following rules **are always active regardless of task scale**, including one-off scripts and demos in exempt scenarios:

| Rule | Description |
|------|-------------|
| Never swallow errors | Caught exceptions must be handled or re-thrown; empty catch/except is forbidden |
| No magic numbers/strings | Constants must be named; bare `if status == 3` is forbidden |
| Accurate function naming | Function names must reflect their behavior; misleading names are forbidden |
| Always validate parameters | Validate parameter validity at public interface/function entry points |
| Type declarations | Public functions have explicit parameter and return type declarations (if language supports it) |
| Meaningful logging | Include contextual information; `print("error")` style logging is forbidden |
| Explicit dependency declaration | External dependencies passed as parameters; implicit global state access inside functions is forbidden |
| Side effect isolation | Functions with side effects (I/O, state mutations, network) are separated from pure computation |

---

## §5 — Proactive Anti-Pattern Detection

Principle checks are not only for review checkpoints. **While writing or reading code in any workflow step**, surface clear violations immediately rather than waiting for the end-of-step checklist.

### When to intervene

Intervene when you spot one of the patterns below with **high confidence** — meaning the violation is structural and detectable from the code itself, not a judgment call that depends on missing context.

| Anti-Pattern | Recognition Signal | Notes |
|---|---|---|
| SRP violation | Describing the function requires "and" / "also" / "as well as" | Flag when the split is obvious, not when it's debatable |
| Layer violation | Business logic inside Entry layer; data access inside Logic layer | Detectable from imports and call targets |
| Swallowed exception | Empty `catch` / `except` block | Zero tolerance — always flag regardless of task scale |
| Magic value | Bare literal in a conditional (`if status == 3`) | Always flag |
| YAGNI over-engineering | Interface or abstraction layer with exactly one implementation | Flag only when no second impl exists or is explicitly planned |
| Hidden dependency | Global state accessed inside a function body without injection | Always flag |
| DRY violation | Identical logic block appearing 2+ times in the same file | Flag on second occurrence; for cross-file duplication, flag only when the function signatures are identical AND the logic body exceeds 10 lines |
| Principle conflict | DRY fix would violate a layer boundary | Name the conflict; apply §2.5 arbitration and explain the verdict |

**Do not intervene** in these situations:
- The violation is debatable or context-dependent
- You are in an exempt scenario (§0.3) — flag only §4 floor-rule violations
- The task is lightweight — flag only clear §4 violations; don't interrupt flow for architectural observations
- You already flagged the same issue in the current response — do not repeat

### How to intervene

One line, inline, non-blocking:

```
⚠️ SRP: `process_order` handles both validation and payment — consider splitting into two functions.
⚠️ Layer: DB query inside `OrderController.create` — should move to Repository layer.
⚠️ Exception swallowed: empty `except` in `parse_config` — handle or re-raise.
```

Format: `⚠️ <Principle>: <what was observed> — <one-line suggestion>`

- Place the flag where you naturally reference the code, not at the end of a long response
- Do not explain the principle definition — just name it
- If a quick, safe fix is obvious, apply it and note what you changed
- If the fix requires design decisions or scope expansion, flag and ask before acting
- If the user dismisses the flag or moves on, do not repeat it

---

## §6 — Communication Standards

- For public interface or cross-module changes, first briefly outline the plan, confirm, then execute; lightweight changes can be implemented directly
- When requirements conflict with principles, first point out the conflict, provide a compliant solution, then ask if the user insists
- When architecture review finds issues, list them for the user to decide; don't make unilateral decisions
- When change scope exceeds expectations (affecting other modules), proactively inform the user of the impact before acting
- When suggesting design patterns, explain the specific problem being solved; don't hard-sell complex solutions
- When over-engineering risk is identified, proactively question it; target minimum maintenance cost
