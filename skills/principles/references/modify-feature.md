# Modify Existing Feature / Module Workflow

> This file is loaded on demand by the `coding-principles` Skill when a modify, enhance, or refactor task is identified. General coding principles (SOLID, DRY, baseline rules, etc.) are in the main SKILL.md and are not repeated here.

---

## Core Principle

Modification requests are riskier than additions — you're touching a running system; pulling one thread affects the whole. The core strategy is **understand first, analyze, then refine, and only then act**.

---

## Complete Execution Workflow

### Step 1: Read the Code — Establish Full Context

> Required for medium and above tasks. Lightweight tasks (minor single-function adjustments) can be simplified to just reading the target function itself.

Before acting, you must build a complete understanding of the target code and its surroundings.

**Questions to answer:**
- What is the **responsibility boundary** of the target code? Which layer does it belong to?
- What are its **callers**? (Who uses it — trace upward)
- What are its **dependencies**? (What does it use — trace downward)
- Is it **indirectly depended upon by other modules via events/callbacks/interfaces**?
- What is the **design intent** of the current code? (Read comments, commit messages, PR descriptions)
- Are there **implicit contracts**? (e.g., return value format, call order, state assumptions)

🔗 When GitNexus is available, see `tool-gitnexus.md` §4.3 "Modify Feature / Step 1 — Read the Code and Build Context" for the enhanced tool-call path and what still requires manual reading.

```
Reading Scope (must cover)
─────────────────────────────────────────────
[ ] Complete implementation of the target function/class/module itself (🔗 context returns code location for direct reading)
[ ] Direct callers (at least one level up) (🔗 context callers)
[ ] Direct dependencies (at least one level down) (🔗 context callees)
[ ] Related interface definitions / abstract base classes / type declarations (🔗 context heritage)
[ ] Related config items / constant definitions (🔗 query for config-related code)
[ ] Related unit tests / integration tests (if any) (🔗 query "<function name> test")
─────────────────────────────────────────────
```

**Why reading is so important:**
Acting without reading is like modifying plumbing without a floor plan — you might fix the kitchen leak but flood the adjacent bathroom. Many "fix introduced a new bug" incidents have root causes in insufficient knowledge of surrounding code.

### Step 2: Impact Analysis — Map the Change Radiation

> Required when involving public interfaces, cross-module changes, or shared data structures. Can be simplified for pure internal logic adjustments.

The goal is to clearly understand "what will be affected if this changes" before acting.

**Analysis dimensions:**
- **Direct impact**: Behavioral changes to the modified function/class itself
- **Upstream impact**: Do callers depend on the behavior that is about to change (return value, exception type, side effects)?
- **Downstream impact**: Does the way dependencies are used need to be adjusted synchronously?
- **Cross-module impact**: Are other modules associated through event bus, shared state, or shared DTOs?
- **Contract impact**: Do the interface signature, parameter types, or return structure change (is it a Breaking Change)?
- **Data impact**: Does it involve database schema changes, cache invalidation, or data migration?

🔗 When GitNexus is available, see `tool-gitnexus.md` §4.3 "Modify Feature / Step 2 — Impact Analysis" for the enhanced tool-call path.

**Output format:**
```
Change Impact Analysis Report
─────────────────────────────────────────────
Change target: <module/function name>
Change type: [ ] Behavior modification  [ ] Signature change  [ ] Internal refactor  [ ] Extension enhancement

Direct impact scope:
  - <list modified files/functions> (🔗 impact Depth 1)

Indirect impact scope:
  - <list affected callers/dependents> (🔗 impact Depth 2+)

Is it a Breaking Change: Yes / No
Does it require synchronous changes to other modules: Yes (list) / No (🔗 determined by cluster boundary)
Does it involve data changes: Yes (describe) / No
Risk level: Low / Medium / High
─────────────────────────────────────────────
```

### Step 3: Requirements Refinement — Re-examine Requirements Under Existing Architecture Constraints

Don't directly implement after receiving requirements — use the established code context to validate and refine them.

**Questions to confirm:**
- In the current architecture, where is **the most natural implementation point** for the behavioral change described in the requirements?
- Can the requirements be achieved through **extending existing abstraction points**, or must core logic be modified?
- Do the requirements conflict with existing design intent? If so, are the requirements unreasonable or does the design need to evolve?
- Are the boundary conditions of the requirements clear? (Scenarios not mentioned in the original requirements — do they exist in the context of the existing code?)

**Core principle: Prioritize finding an "extension-based modification" path; only then consider "invasive modification."**

🔗 When GitNexus is available, see `tool-gitnexus.md` §4.3 "Modify Feature / Step 3 — Find Extension Paths" for the enhanced tool-call path.

```
Modification Strategy Priority (best to worst)
─────────────────────────────────────────────
1. Configuration: Modifying config/params is sufficient → zero code changes
2. Extension: Add implementation class/strategy/handler, register with existing extension point → don't touch old code
3. Decoration: Wrap existing behavior with decorator/middleware/AOP → old code is unaware
4. Local modification: Modify logic inside existing function/method → minimal change principle
5. Signature change: Need to modify interface/parameters/return value → must synchronize all callers
6. Structural reorganization: Need to split/merge/move modules → requires explicit user authorization
─────────────────────────────────────────────
```

**Strategy selection examples:**

| Requirement Scenario | Recommended Strategy | Reason |
|---------------------|---------------------|--------|
| "Support new export format" | Extension (add export strategy class) | Existing strategy interface; new addition doesn't change old code |
| "Adjust calculation formula" | Local modification | Only internal logic change; doesn't affect interface |
| "Add field to interface response" | Signature change (confirm first) | May be a Breaking Change |
| "Split user module into auth and profile modules" | Structural reorganization (requires authorization) | Large-scale change; user must be informed |
| "Skip execution of a feature under certain conditions" | Configuration / Decoration | Implement through config switch or decorator |

### Step 4: Solution Design — Create Modification Plan and Get Confirmation

> Confirm first when involving public interfaces, cross-module changes, or Breaking Changes. Lightweight internal logic adjustments can be implemented directly.

Before acting, inform the user of:
- Which modification strategy is being used (corresponding to the priority in Step 3)
- Specifically which files/functions will be changed, and how
- Expected impact scope (from Step 2 analysis)
- Whether there are risk points that need special attention

**Confirmation template:**
```
Modification Plan
─────────────────────────────────────────────
Requirement summary: <one-sentence description>
Modification strategy: <Configuration / Extension / Decoration / Local modification / Signature change / Structural reorganization>

Change list:
  1. <File A> - <change description>
  2. <File B> - <change description>

Impact scope: <directly/indirectly affected modules> (🔗 from Step 2 impact analysis)
Breaking Change: Yes / No
Risk points: <if any>

Confirm execution?
─────────────────────────────────────────────
```

### Step 5: Implement — Follow the Minimal Change Principle

> ⚠️ **All principles in SKILL.md (SOLID, DRY, baseline rules, etc.) apply to every line of code written in this step — satisfy them as you write, not as an afterthought.**

**Execution discipline:**

- **Maintain style consistency**: Naming, indentation, comment language fully consistent with surrounding code
- **No hitchhiking**: Don't "optimize" unrelated code while implementing requirements; each change serves only one purpose
- **Changes are traceable**: Add comments explaining the reason for non-trivial modifications and temporary compatibility logic, format: `# change: <requirement description> - <reason for change>`
- **Backward compatibility**: If public interfaces are modified, prefer compatible approaches (default parameters, overloading, adapters); unless the user explicitly states backward compatibility is not needed (e.g., major version upgrades, deprecating old interfaces), in which case mark the Breaking Change and reason in comments
- **Incremental implementation**: Do structural adjustments first, then behavioral changes; logically separable changes are not mixed together

**Common backward compatibility approaches:**
```python
# ✅ Add optional parameter, old calling style unaffected
def process_order(order_id: str, priority: int = 0):  # priority is newly added
    ...

# ✅ Keep old function as adapter, internally calls new implementation
def get_user(user_id):                    # Old interface, preserved
    return get_user_v2(user_id).to_legacy_format()

def get_user_v2(user_id) -> UserDTO:      # New interface
    ...

# ✅ Mark with @deprecated rather than deleting directly
@deprecated("Use get_user_v2 instead, will be removed in v3.0")
def get_user(user_id): ...
```

**❌ Forbidden actions:**
- Modifying public interface signatures without confirmation
- Sneaking in "optimizations" unrelated to the current requirement
- Deleting code that's temporarily unused but potentially useful without informing the user
- Changing return value structures without updating all callers

🔗 When GitNexus is available, see `tool-gitnexus.md` §4.3 "Modify Feature / Step 5 — Signature Change Safety Net" for the enhanced tool-call path.

### Step 6: Compliance Audit (Required for Medium and Above Tasks)

```
Modification Architecture Audit Checklist
─────────────────────────────────────────────────────
[ ] Does the change follow the minimal change principle? Any unnecessary extra changes?
[ ] Is style consistency with surrounding code maintained?
[ ] Has the existing interface contract been broken? (Parameters, return values, exceptions)
[ ] Have all callers been adapted to the change? Any missed?
[ ] Has any new circular dependency been introduced?
[ ] Has the encapsulation boundary of existing modules been broken?
[ ] Is the dependency direction still compliant? Any new reverse dependencies?
[ ] Are there conflicts with adjacent features? (Shared state, events, shared data structures)
[ ] Do the original unit tests still pass? Do tests need to be updated?
[ ] Does documentation / comments / type definitions / CHANGELOG need to be updated?
─────────────────────────────────────────────────────
```

🔗 When GitNexus is available, see `tool-gitnexus.md` §4.3 "Modify Feature / Step 6 — Compliance Audit" for the enhanced tool-call path and what still requires manual review.

Audit results must be clearly communicated to the user: **Passed ✅** or **Issues found ⚠️ (with specific details and impact scope)**.

---

## Workflow Tailoring Guide by Task Scale

Not every modification requires running through all 6 steps. The following are tailoring recommendations by task scale:

### Lightweight Modification (Minor single-function logic adjustment, changing config values, style adjustments)

```
Required: Step 5 (implement, follow baseline rules)
Optional: Step 1 (quick scan of target function; 🔗 can use context for quick lookup)
Skip: Steps 2-4, Step 6
```

### Medium Modification (Modify module internal logic, add/remove internal functions, adjust data processing flow)

```
Required: Step 1 (read) → Step 5 (implement) → Step 6 (audit)
          🔗 When GitNexus available: Step 1 uses context instead of manual reading, Step 6 uses impact for assisted review
Optional: Step 3 (requirements refinement, recommended for complex logic changes)
Skip: Step 2 (no cross-module impact), Step 4 (no confirmation needed)
```

### Large Modification (Cross-module changes, public interface modifications, Breaking Changes, architecture adjustments)

```
Required: All 6 steps, executed in order
          🔗 When GitNexus available: Steps 1-2 tool-driven, Step 6 semi-automated review
No skippable items
```

---

## Common Pitfalls

| Pitfall | Description | Correct Approach | 🔗 GitNexus Detection |
|---------|-------------|-----------------|----------------------|
| Act without reading | Modified function behavior without reading callers | At minimum trace one level up to confirm caller dependencies | `context` returns complete caller list in one call |
| Hitchhiking | Smuggled in "opportunistic optimizations" during requirement modification | Strict separation: this change only serves what the requirement asks | — |
| Implicit Breaking Change | Changed return value structure but assumed "callers shouldn't be affected" | Proactively check all callers; when in doubt, confirm | `impact upstream` precisely lists all callers |
| Over-modification | User requested minor adjustment but entire module was rewritten | Follow minimal change principle; rewrite requires user authorization | — |
| Forgot compatibility | Directly changed signature when modifying public interface | Prefer default parameters/overloading to maintain compatibility | `impact upstream` to check number of affected callers |
| Missed sync | Changed code but forgot to update related docs/types/tests | Audit checklist includes sync check items | `query "<function name> test"` to search related tests |
| State pollution | Modified shared state structure but other readers not adapted | Impact analysis includes shared state check | `query` to search all consumers of shared structure |

---

## Reply Format

End every modify-feature response with this block (omit a field only if it genuinely has nothing to report):

```
─── Modification Summary ────────────────────────────────
① Conclusion:         <one sentence: what changed, which strategy was used, and the outcome>
② Changes:            <files / functions modified; callers updated; backward-compat shims added>
③ Risks / Assumptions: <Breaking Change status; compatibility assumptions; callers not yet adapted>
④ Verification:       <Step 6 audit result: Passed ✅ / Issues ⚠️ (details); unit test status>
⑤ Needs your input:   <Breaking Change approval; callers that must still be updated by the user>
────────────────────────────────────────────────────────
```
