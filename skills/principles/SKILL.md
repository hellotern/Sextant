---
name: sextant
description: General coding principles for software engineering tasks that don't match a more specific sextant sub-skill. Use as fallback for general coding work, or when the task is lightweight (config changes, style fixes, utility functions, one-off scripts). For specific task types, the dedicated sub-skills take priority: sextant-fix-bug, sextant-add-feature, sextant-modify-feature, sextant-review-code, sextant-write-tests, sextant-refine-requirements, sextant-debug, sextant-ship, sextant-migrate, sextant-security, sextant-plan.
---

# General Coding Principles

> **Core Goal: Make code easy to read, modify, and extend.** When principles conflict, the final arbitration standard is "lowest long-term maintenance cost for the team." Standards are tools, not chains.

---

## §0 — Code Quality Baselines (Always Active)

The following rules **are always active regardless of task scale**, including one-off scripts and demos in exempt scenarios:

| Rule | Description |
|------|-------------|
| Never swallow errors | Caught exceptions must be handled or re-thrown; empty catch/except is forbidden |
| No magic numbers/strings | Constants must be named; bare `if status == 3` is forbidden |
| Accurate function naming | Function names must reflect their behavior; misleading names are forbidden |
| Always validate parameters | Validate parameter validity at public interface/function entry points |
| Type declarations | Public functions have explicit parameter and return type declarations (if language supports it) |
| Meaningful logging | Include contextual information; `print("error")` style logging is forbidden |
| Explicit dependency declaration | External dependencies passed as parameters; implicit global state access inside functions is forbidden. *(Lightweight tasks: flag only direct global state access — singletons, hardcoded config reads; skip constructor injection analysis, which belongs to §6.1)* |
| Side effect isolation | Functions with side effects (I/O, state mutations, network) are separated from pure computation |

> **Lightweight task? §0 + §2 fully active; §1 limited to §0 violations only (architectural flags suppressed) — skip §3, §4, §5, §6.**
> Medium/large tasks: continue reading.

---

## §1 — Proactive Anti-Pattern Detection (Always Active)

Principle checks are not only for review checkpoints. **While writing or reading code in any workflow step**, surface clear violations immediately rather than waiting for the end-of-step checklist.

### When to intervene

Intervene when you spot one of the patterns below with **high confidence** — meaning the violation is structural and detectable from the code itself, not a judgment call that depends on missing context.

| Anti-Pattern | Recognition Signal | Notes |
|---|---|---|
| SRP violation | Describing the function requires "and" / "also" / "as well as" | Flag when the split is obvious, not when it's debatable |
| Layer violation | Signal varies by paradigm (§6.0): backend — business logic in Entry / DB access in Logic; frontend — store imported inside atom component; CLI — I/O inside core logic; FP — I/O inside pure-core function | Detectable from imports and call targets |
| Swallowed exception | Empty `catch` / `except` block | Zero tolerance — always flag regardless of task scale |
| Magic value | Bare literal in a conditional (`if status == 3`) | Always flag |
| YAGNI over-engineering | Interface or abstract class with exactly one implementation **and** no comment/doc/issue referencing a planned second implementation | Flag when both conditions are true — one impl AND no evidence of a planned second |
| Hidden dependency | Global state accessed inside a function body without injection | Always flag |
| DRY violation | Identical logic block appearing 2+ times in the same file | Flag on second occurrence; for cross-file duplication, flag only when the function signatures are identical AND the logic body exceeds 10 lines |
| Principle conflict | DRY fix would violate a layer boundary | Name the conflict; apply §5.5 arbitration and explain the verdict |

**Do not intervene** in these situations:
- The violation is debatable or context-dependent
- You are in an exempt scenario (§3.3) — flag only §0 floor-rule violations
- The task is lightweight — flag only clear §0 violations; don't interrupt flow for architectural observations
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

## §2 — Communication Standards

- For public interface or cross-module changes, first briefly outline the plan, confirm, then execute; lightweight changes can be implemented directly
- When requirements conflict with principles, first point out the conflict, provide a compliant solution, then ask if the user insists
- When architecture review finds issues, list them for the user to decide; don't make unilateral decisions
- When change scope exceeds expectations (affecting other modules), proactively inform the user of the impact before acting
- When suggesting design patterns, explain the specific problem being solved; don't hard-sell complex solutions
- When over-engineering risk is identified, proactively question it; target minimum maintenance cost

---

## §3 — Task Identification and Rule Activation

### 3.0 Environment Detection and Tool Enhancement

Before starting any coding task, **first check whether the current project has GitNexus integrated**:

**Detection method:** Check whether a `.gitnexus/` directory exists in the project root, or whether the current environment can call GitNexus MCP tools (such as `context`, `impact`, `query`).

**Detection result:**
- **GitNexus available** → The `tool-gitnexus/SKILL.md` reference is automatically injected by the sub-skill's dynamic injection. In subsequent steps, all steps marked 🔗 should prioritize MCP tool calls over manual reading and grep searches.
- **GitNexus unavailable** → Ignore all 🔗 markers and follow the original workflow. No existing workflow is affected.

> **Fallback skill note:** When `sextant` (this file) is loaded directly as the fallback skill — rather than via a sub-skill — there is no automatic GitNexus injection. If you detect that `.gitnexus/` exists in the project root, apply the GitNexus guidance from `tool-gitnexus/SKILL.md` for any steps marked 🔗.

> GitNexus is an accelerator, not a prerequisite. All workflows work fully without GitNexus; with GitNexus, efficiency and precision are higher.

### 3.1 Sub-Skill Ecosystem

Specific task types are handled by dedicated sub-skills — each self-contained with full workflow:

| Task Type | Sub-skill |
|-----------|-----------|
| Bug Fix | `sextant-fix-bug` |
| New Feature / New Module | `sextant-add-feature` |
| Modify / Enhance / Refactor | `sextant-modify-feature` |
| Code Review | `sextant-review-code` |
| Write Tests | `sextant-write-tests` |
| Requirements Analysis | `sextant-refine-requirements` |
| Debug (symptom known, location unknown) | `sextant-debug` |
| Ship / PR Preparation | `sextant-ship` |
| Migration (multi-module, versioned) | `sextant-migrate` |
| Security Audit | `sextant-security` |
| Sprint Planning | `sextant-plan` |
| General Coding / Lightweight tasks | ← this skill |

**This skill applies when:** the task is general coding, lightweight (config change, utility function, style fix), or explicitly exempt (prototype, one-off script, algorithm problem, pure explanation).

**Negative Triggers** — apply only §0 baseline rules or nothing at all:

- Algorithm / puzzle problems with no existing codebase context ("implement quicksort", "solve this leetcode problem")
- Pure explanation requests with no modification intent ("what does this code do?", "explain how X works")
- Trivial one-liners ("write a regex to match emails", "write hello world in Python")
- One-off scripts explicitly scoped as throwaway ("write a bash script to rename these files")
- User explicitly signals low quality bar: "prototype", "quick and dirty", "doesn't need to be production quality", "just a draft"

### 3.2 Assess Task Scale and Activate Rules Accordingly

The rules in this Skill are **not executed in full every time**, but are activated in tiers based on task scale:

**Lightweight tasks** (adjustments within a single function, config changes, style fixes, utility function writing)
Apply §0 baseline rules, keep §1 detection limited to clear §0 violations, and follow §2 direct-execution communication. Skip the heavier §3–§6 analysis path.

**Medium tasks** (add functions/classes, modify module internal logic, bug fixes)
Additionally activate: SRP, DRY, interface contracts (parameter validation, return type), read all direct callers to confirm no breakage.

**Large tasks** (cross-module changes, public interface modifications, new modules, architecture adjustments)
Full activation: complete SOLID review, impact analysis, confirm plan before implementation, architecture compliance audit.

**Assessment tips:** Watch for two signals — (1) Does the change cross file boundaries? (2) Does it involve public interface / shared data structure changes? If either is yes, treat it as at least "medium."

**Impact Radius Scorecard** — use when the scale judgment is ambiguous. Score the change on the five factors below (max 10), then map the total to a tier. This is an overlay on the qualitative tiers above; the tiers themselves do not change.

| Factor | 0 | 1 | 2 |
|--------|---|---|---|
| Files changed | 0 | 1–2 | 3+ |
| Public interfaces changed | 0 | 1 | 2+ |
| Dependency direction change | None | New dependency added | Cross-layer or reverse dependency |
| Data structure change | None | New field added | Field modified / deleted / schema changed |
| Downstream blast radius | No callers / dependents affected | 1–3 callers or dependents need updating | 4+ callers, or cross-team / cross-service impact |

Score → Tier mapping (max score = 10):
- **0–3** → Lightweight
- **4–6** → Medium
- **7–8** → Large
- **9–10** → Architectural — pause implementation; produce an architecture decision record first

Output format when used: `Impact radius: N (<factor summary>) → <Tier>.`

### 3.3 Exempt Scenarios and Early Exit

The following scenarios can relax or even skip most rules, **retaining only the baseline rules** (§0). §1's detection engine remains active but scoped to §0 violations only — architectural flags (SRP, layer, DRY) are suppressed in exempt scenarios.
- One-off scripts / temporary tools
- Demos / prototypes / POCs
- Algorithm problems / competitive programming
- Notebooks / data exploration
- User explicitly asks for "code first, architecture discussion later"
- User explicitly asks for minimal implementation / quick delivery

**Mid-process early exit:** If the user interrupts at any workflow step with phrases like "just write it", "skip the analysis", "just do it", or "stop explaining and implement" — immediately jump to the implementation step and apply only the baseline rules (§0). Do not insist on completing earlier steps. Briefly acknowledge the shortcut (e.g., "Skipping analysis, implementing directly.") and proceed.

---

## §4 — SOLID Principles

### SRP — Single Responsibility

Each module, class, and function does **one thing** and has **one reason to change**.

**Assessment tip:** Describe the responsibility in one sentence. If "and," "as well as," or "also" appears, it usually needs to be split.

**Layered responsibilities — backend MVC/Clean example** (see §6.0 for frontend, CLI, and functional paradigm mappings; no layer-crossing allowed in any paradigm):
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

## §5 — DRY, YAGNI, and Design Patterns

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

## §5.5 — Principle Arbitration

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

### §0 Baseline vs Minimal-Change — a baseline fix would expand the diff

**Scenario:** While fixing a bug or making a small modification, you notice adjacent code that violates §0 baseline rules (missing type declarations, magic numbers, absent parameter validation). Fixing those violations would expand the diff beyond the task scope.

**Verdict: Minimal-change wins, with one hard exception.**

Apply §0 baseline rules only to code you are actively writing or directly modifying in this task. For surrounding untouched code, match its existing convention rather than upgrading it.

**Hard exception — always fix regardless of scope:** Empty `catch`/`except` that silently swallows errors. Silent failure masking is the one §0 rule that overrides minimal-change because it actively hides bugs from future debugging.

**For all other §0 violations in surrounding code:** raise a `⚠️` flag (per §1) and let the user decide. Do not expand the diff unilaterally.

**Signal to flip:** The user explicitly says "clean this up", "bring this up to standard", or "fix everything you see while you're at it."

### SRP vs Minimal-Change — target function violates SRP but splitting exceeds bug-fix scope

**Scenario:** While fixing a bug, you discover that the target function is a clear SRP violation — 150+ lines doing validation, business logic, and persistence in one body. Splitting it would be the right architectural move, but it would far exceed the scope of the bug fix and introduce new regression risk.

**Verdict: Minimal-change wins. Fix the bug; flag the SRP violation.**

Fix only the code that causes the bug. Do not refactor the function as part of the bug fix. Raise one `⚠️` SRP flag (per §1) so the violation is visible, then stop.

**Reasoning:** A bug fix has a clear success condition: the bug no longer reproduces and no regression is introduced. An SRP refactor changes the observable structure of the code and requires its own impact analysis, caller review, and test updates. Mixing the two makes both harder to review and increases the probability of shipping a new defect alongside the fix.

**Signal to flip:** The user explicitly authorizes the refactor ("clean this up while you're at it", "go ahead and split it"), or the SRP violation is the direct cause of the bug — meaning the fix cannot be made safely without first untangling the responsibilities.

### Performance vs Readability — optimization that obscures intent

**Scenario:** An inline optimization measurably boosts throughput, but the resulting code is significantly harder to read or maintain.

**Verdict: Readability wins** — unless the profiler confirms this is a hot path AND the optimization is encapsulated inside a clearly named function.

**Reasoning:** Most code is not on the hot path. Optimizing unconfirmed bottlenecks pays a permanent readability tax for speculative performance gains. A named function preserves intent even when the implementation is non-obvious.

**Signal to flip:** Profiler data shows the path is a measurable bottleneck (not just "feels slow"), AND the optimization is wrapped in a helper with a name that explains its purpose (e.g., `fast_path_sort_by_key`).

### Security vs Convenience — strict validation increases friction

**Scenario:** Adding strict input validation, authentication checks, or access controls increases development friction or adds boilerplate to callers.

**Verdict: Security wins.** Do not trade security guarantees for developer convenience.

**Reasoning:** Security failures compound: a single breach can expose all users. Developer friction is a one-time setup cost. The convenience-security tradeoff is asymmetric — convenience saves minutes; a security gap can cost weeks of incident response.

**Signal to flip:** The environment is an explicitly documented, network-layer-enforced trusted intranet (e.g., inter-service calls inside a private VPC with mutual TLS). The relaxation must be documented and must not apply at any externally reachable surface.

### Consistency vs Local Optimum — a module uses a locally superior pattern that conflicts with global style

**Scenario:** A module could use a pattern better suited to its local context, but that pattern conflicts with the conventions used throughout the rest of the codebase.

**Verdict: Consistency wins.** Follow the established codebase convention.

**Reasoning:** A reader moving between modules pays a higher cognitive overhead tax than the local optimization saves. Convention is a communication protocol — diverging from it without a documented reason silently raises the cost of onboarding and navigation for every future contributor.

**Signal to flip:** The subsystem is truly isolated — it has independent team ownership, is deployed or versioned independently, and has a documented rationale for the divergence. All three conditions must hold.

### Test Coverage vs Delivery Speed — deciding what tests are non-negotiable

**Scenario:** Time pressure pushes toward shipping with reduced test coverage.

**Verdict: Conditional** — not every test is equally non-negotiable.

**Non-skippable (never trade away):**
- Bug reproduction tests (a test that would have caught this bug before)
- Public interface contract tests (callers depend on this behavior)
- Logic with multiple callers (shared behavior; breakage has wide blast radius)

**Skippable under time pressure (low blast radius):**
- Happy-path integration tests for internal-only changes with no public surface
- Coverage-padding tests for trivial helpers (pure single-operation functions)

**Reasoning:** The non-skippable category covers tests that catch regressions in shared contracts and public surfaces — exactly the failures most expensive to debug in production. The skippable category covers tests whose primary value is local confidence, which can be deferred.

**Signal to flip for skippable items:** The delivery pressure passes; these tests should be written in a follow-up task (not indefinitely deferred).

### Backward Compatibility vs Tech Debt Removal — public interface carries debt

**Scenario:** A public interface has accumulated tech debt (confusing naming, awkward parameter order, implicit assumptions). Cleaning it up requires a breaking change.

**Verdict: Backward compatibility wins.** Do not make unilateral breaking changes to public interfaces.

**Reasoning:** Breaking external consumers without notice destroys trust and causes production incidents. Internal tech debt has bounded blast radius — it hurts the team that owns it. A breaking change to a public interface has unbounded blast radius — it breaks every consumer, including ones you don't know about.

**Required path for breaking changes:** provide a `@deprecated` shim that preserves the old interface, document the migration path, set a sunset timeline, and notify known consumers before removing the shim.

**Signal to flip:** A major version bump is in progress AND all known consumers have been notified AND a migration path + deprecated shim are in place. All three conditions must hold before the old interface can be removed.

---

## §6 — Architecture Constraints (Always Active)

### 6.0 Architecture Paradigm Detection and Adaptation

The layered backend model used as the default example throughout §4 and §6.2 is **one paradigm among several**. Core principles (SRP, DIP, OCP, layer boundaries) apply universally — but their concrete expressions differ. Before applying architectural constraints, identify which paradigm the project uses.

**Detection signals:**

| Signal | Paradigm |
|--------|----------|
| Dirs like `controllers/`, `services/`, `repositories/`; HTTP handlers at the entry point | **Backend layered** (MVC / Clean Architecture) |
| Dirs like `components/`, `hooks/`, `store/`, `pages/`; UI rendered from a component tree | **Frontend component tree** (React / Vue / Svelte) |
| Entry point is a CLI `main` with subcommands; primary output is stdout / stderr / files | **CLI / script** |
| No classes; logic expressed as pipelines of pure functions; data is immutable records | **Functional** (FP — Haskell, Elixir, or FP-style TS/Python) |
| Dirs like `packages/`, `apps/`, `libs/`; workspace config (`pnpm-workspace.yaml`, `lerna.json`, `nx.json`) | **Monorepo / multi-package** |
| Dirs like `handlers/`, `consumers/`, `producers/`; Kafka / RabbitMQ / EventBridge client libraries; message schema definitions | **Event-driven** (Kafka / RabbitMQ / EventBridge) |
| `handler.py` / `exports.handler` entry points; no long-running process; API Gateway or event-source triggers | **Serverless / Functions** (AWS Lambda / GCP Cloud Functions) |
| Dirs like `training/`, `inference/`, `experiments/`; `.ipynb` files; model checkpoint files; data pipeline DAGs | **AI/ML pipeline** (PyTorch / TensorFlow / MLflow) |

**Paradigm adaptation table:**

| Paradigm | SRP unit | Layering equivalent | DIP — without class injection | OCP — extend without modifying |
|---|---|---|---|---|
| **Backend layered** | Class / Service / Repository | `Entry → Logic → Data → Infra` | Constructor injection of abstract types (interface / ABC) | Strategy pattern / plugin registry |
| **Frontend component tree** | Component / custom hook / store slice | `Page → Feature component → Atom component`; hooks own local state, store owns shared state | Pass data and callbacks via props or context; atoms must not import the store directly | New component variant, render prop, or HOC — do not modify existing atoms |
| **CLI / script** | Subcommand handler / pure function | `CLI entry → command handler → core logic → I/O adapters` | Pass I/O handles (stdin, stdout, file path) as function parameters; never hardcode `sys.stdout` inside core logic | New subcommand registered to the dispatch table; existing commands untouched |
| **Functional (FP)** | Pure function / module | `I/O boundary → pure core → data transformers` | Higher-order functions; partial application; pass behavior as function arguments instead of injecting objects | Compose new behavior by chaining existing functions; avoid adding a new branch inside an existing function body |
| **Monorepo / multi-package** | Package / module | `app packages → domain packages → shared packages → infra packages` | Declare cross-package dependencies via the workspace's dependency mechanism (`workspace:*` in JS/TS, path dependencies in Python/Rust, replace directives in Go); packages must not reach into another package's internals | Add a new package rather than modifying an already-published package; use shared packages for cross-cutting concerns |
| **Event-driven** | Event handler / consumer function | `Event publisher → Event bus → Consumer → Handler → Side-effect adapter` | Pass event bus as an injected dependency; handlers must not instantiate the bus directly | New event type handled by a new consumer registered to the bus; existing consumers untouched |
| **Serverless / Functions** | Function handler | `Trigger / event source → Handler → Core logic → I/O adapters` | Pass config, clients, and I/O handles as parameters; never read `process.env` / `os.environ` inside core logic — read at the handler boundary only | New function added to dispatch config; existing functions untouched; shared logic extracted to a utility layer |
| **AI/ML pipeline** | Pipeline stage / transform function | `Data ingestion → Preprocessing → Model → Evaluation → Serving` | Pass data sources, model artifacts, and config as parameters; pipeline stages must not read from hardcoded paths | New stage added to the pipeline; existing stages unchanged; data contracts (schemas) defined in a shared layer |

**When paradigm is mixed or unclear:** Apply the backend layered model to the server/core layer, and the frontend component model to the UI layer. If the project combines both, identify each subsystem's paradigm separately and apply the corresponding row.

### Paradigm Operational Examples

The same principles from §4 apply in every paradigm; the violation signals just look different.

**Frontend (React/Vue) — SRP & layer violations:**
```tsx
// ❌ Atom component imports store directly — layer violation (store is shared state layer)
function Avatar({ userId }) {
    const user = useUserStore(s => s.users[userId])  // atom must not reach into store
    return <img src={user.avatar} />
}

// ✅ Data passed via props; atom stays presentational
function Avatar({ avatarUrl }) {
    return <img src={avatarUrl} />
}

// ❌ API call inside presentational component — SRP violation
function UserCard({ userId }) {
    const [user, setUser] = useState(null)
    useEffect(() => { fetch(`/api/users/${userId}`).then(...) }, [userId])  // wrong layer
    ...
}

// ✅ Data-fetching in a custom hook (or feature component); atom receives data
function useUser(userId) { ... }     // hook owns data-fetching
function UserCard({ user }) { ... }  // atom just renders
```

**CLI / Script — SRP & I/O layer violations:**
```python
# ❌ I/O (print) inside core logic — layer violation
def calculate_tax(income: float) -> float:
    result = income * 0.3
    print(f"Tax calculated: {result}")  # I/O belongs in the CLI entry layer
    return result

# ✅ Core logic is pure; I/O only at the CLI entry layer
def calculate_tax(income: float) -> float:
    return income * 0.3

def main():
    result = calculate_tax(float(sys.argv[1]))
    print(f"Tax calculated: {result}")

# ❌ Hardcoded file path inside core logic — hidden dependency
def load_config():
    return yaml.load(open("config.yaml"))  # caller cannot inject a different source

# ✅ I/O handle passed as parameter
def load_config(stream: IO) -> dict:
    return yaml.safe_load(stream)
```

**Functional (FP) — SRP & purity violations:**
```haskell
-- ❌ I/O inside pure-core function — layer violation
processOrder :: Order -> IO ProcessedOrder
processOrder order = do
    logInfo "processing"          -- I/O inside what should be pure logic
    pure $ applyDiscount order

-- ✅ Pure core; I/O composed at the boundary
applyDiscount :: Order -> ProcessedOrder   -- pure, testable
applyDiscount order = ...

processOrder :: Order -> IO ProcessedOrder
processOrder order = do             -- I/O boundary wraps pure call
    logInfo "processing"
    pure $ applyDiscount order
```

```python
# ❌ New branch added inside existing function — OCP violation (FP style)
def format_value(v):
    if isinstance(v, str): return v.strip()
    if isinstance(v, int): return str(v)
    if isinstance(v, list): return ",".join(v)   # new type → modified old function

# ✅ Extend by composing; dispatch table replaces branching
FORMATTERS = {str: str.strip, int: str, list: lambda v: ",".join(v)}
def format_value(v):
    return FORMATTERS.get(type(v), str)(v)
# Adding a new type: add one entry to FORMATTERS, existing code unchanged
```

**Event-driven — SRP & dependency violations:**
```python
# ❌ Event bus instantiated inside handler — hidden dependency (DIP violation)
class OrderCreatedHandler:
    def __init__(self):
        self._bus = KafkaEventBus("localhost:9092")  # handler pulls its own bus

    def handle(self, event: OrderCreatedEvent):
        self._bus.publish("inventory.reserve", event.order_id)

# ✅ Event bus injected; handler declares its dependencies
class OrderCreatedHandler:
    def __init__(self, bus: EventBus):  # injected — testable, swappable
        self._bus = bus

    def handle(self, event: OrderCreatedEvent):
        self._bus.publish("inventory.reserve", event.order_id)

# ❌ Business logic inside consumer handler — SRP violation
def on_payment_received(event):
    db.execute("UPDATE orders SET status='paid' WHERE id=?", event.order_id)
    send_confirmation_email(event.customer_email)   # two responsibilities in one handler
    publish_to_fulfillment(event.order_id)

# ✅ Handler delegates to core logic; side effects in adapters
def on_payment_received(event, order_service: OrderService):
    order_service.confirm_payment(event.order_id)  # one responsibility: delegate
```

**Serverless / Functions — layer & hidden dependency violations:**
```python
# ❌ Config read inside core logic — hidden dependency
def calculate_tax(amount: float) -> float:
    rate = float(os.environ["TAX_RATE"])  # core logic reaches into environment
    return amount * rate

# ✅ Config read at handler boundary, injected into core logic
def calculate_tax(amount: float, rate: float) -> float:
    return amount * rate                  # pure, testable

def handler(event, context):
    rate = float(os.environ["TAX_RATE"])  # env read at boundary only
    return calculate_tax(event["amount"], rate)

# ❌ Database client instantiated inside handler — not injectable, not testable
def handler(event, context):
    db = boto3.resource("dynamodb")       # handler owns its own client
    table = db.Table("Orders")
    ...

# ✅ Client passed as parameter (or injected via dependency container)
def handler(event, context, db=None):
    if db is None:
        db = boto3.resource("dynamodb")   # default for production
    process_order(event, db)              # core logic receives the client
```

**AI/ML pipeline — SRP & layer violations:**
```python
# ❌ Data loading inside model training function — layer violation
def train_model(epochs: int):
    df = pd.read_csv("/data/training_data.csv")   # hardcoded path in core logic
    X, y = preprocess(df)
    model.fit(X, y, epochs=epochs)

# ✅ Data loading at pipeline boundary; core logic receives clean data
def train_model(X, y, epochs: int):              # pure training stage
    model.fit(X, y, epochs=epochs)
    return model

def run_pipeline(data_path: str, epochs: int):   # pipeline entry: orchestrates stages
    df = pd.read_csv(data_path)
    X, y = preprocess(df)
    return train_model(X, y, epochs)

# ❌ Preprocessing logic duplicated in training and inference — DRY violation
def train(raw_data):
    normalized = (raw_data - raw_data.mean()) / raw_data.std()   # duplicated
    ...

def predict(raw_input):
    normalized = (raw_input - raw_input.mean()) / raw_input.std()  # same logic
    ...

# ✅ Shared preprocessing stage; both training and inference import it
def normalize(data):                      # single source of truth in shared layer
    return (data - data.mean()) / data.std()
```

### 6.1 Hollywood Principle

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

### 6.2 Dependency Direction Rules

```
Default (backend layered) — see §6.0 for other paradigm mappings:
─────────────────────────────────────────────────────────────
Entry Layer  →  Logic Layer  →  Data Layer  →  Infrastructure Layer

Utility Layer ← Any layer can depend on it,
                but Utility Layer must not depend on business layers
─────────────────────────────────────────────────────────────
```

**Forbidden in every paradigm:** Upward dependencies, circular dependencies, lower-level layers being aware of higher-level concepts.

**Paradigm-specific layer violation signals** (see §6.0 for full mapping):
- Backend: DB access inside Logic layer; business logic inside Controller
- Frontend: store imported directly inside an atom component; API call inside a presentational component
- CLI: `print` / file write inside core logic (not the I/O adapter)
- Functional: I/O performed inside a pure-core function
- Monorepo: app package importing directly from another app package; domain package importing from an infra package; shared package importing from any domain/app package
- Event-driven: business logic executed directly inside a consumer handler instead of delegating to a core logic function; event bus instantiated inside a handler instead of injected
- Serverless: environment variable or config read inside core logic instead of at the handler boundary; database client instantiated inside a handler instead of passed as a parameter
- AI/ML pipeline: data loading or I/O inside a model training function; preprocessing logic duplicated between training and inference pipelines instead of extracted to a shared stage

**Detect circular dependencies:** Use `pydeps` for Python; `madge` for TS/JS. 🔗 When GitNexus is available, `impact({ target: "<module>", direction: "both" })` can directly detect circular and reverse dependencies from the knowledge graph, covering all languages without additional tools.

### 6.3 Module Boundary Rules

- Cross-module communication goes through public interfaces or event buses; direct references to another module's internal implementation are forbidden
- Module internals are private by default; only explicitly marked items are exposed publicly
- Shared data structures (DTO / Event Payload) belong to a dedicated shared layer, not to any single business module
