---
name: sextant-modify-feature
description: Use when changing, enhancing, optimizing, or refactoring existing functionality in the codebase. Stronger signals: "modify", "refactor", "optimize", "improve", "change how X works", "enhance". Use when the thing being changed already exists — if it doesn't exist yet, use sextant-add-feature instead. Apply this skill before starting any modify/refactor work.
---

!`awk 'f;/^---$/{c++}c==2{f=1}' ${CLAUDE_SKILL_DIR}/../principles/SKILL.md`

!`[ -d .gitnexus ] && awk 'f;/^---$/{c++}c==2{f=1}' ${CLAUDE_SKILL_DIR}/../tool-gitnexus/SKILL.md || true`

---

# Modify Existing Feature / Module Workflow

## Disambiguating modify-feature vs fix-bug

> **Use this skill when:** the code does X correctly — you want it to do Z instead (desired behavior is changing).
> **Use fix-bug when:** the code *should* do X but does Y — you want to restore correct behavior.
>
> Quick test: *"Is the current behavior broken, or just not what we want going forward?"*
> → **Broken / was never right** → **stop**. Tell the user: "This looks like a bug rather than a behavior change. Please re-trigger with `sextant-fix-bug` for the correct workflow." Do not proceed with this skill.
> → **Worked correctly, requirements evolved** → modify-feature (continue here).
>
> Edge case: Performance problems and security gaps feel like bugs but are almost always modify-feature — the code "works," it just doesn't meet a non-functional requirement. Continue with this skill.

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

🔗 When GitNexus is available, use `context` MCP tool to get callers and callees automatically.

```
Reading Scope (must cover)
─────────────────────────────────────────────
[ ] Complete implementation of the target function/class/module itself
[ ] Direct callers (at least one level up)
[ ] Direct dependencies (at least one level down)
[ ] Related interface definitions / abstract base classes / type declarations
[ ] Related config items / constant definitions
[ ] Related unit tests / integration tests (if any)
─────────────────────────────────────────────
```

### Step 2: Impact Analysis — Map the Change Radiation

> Required when involving public interfaces, cross-module changes, or shared data structures.

**Analysis dimensions:**
- **Direct impact**: Behavioral changes to the modified function/class itself
- **Upstream impact**: Do callers depend on the behavior that is about to change?
- **Downstream impact**: Does the way dependencies are used need to be adjusted synchronously?
- **Cross-module impact**: Are other modules associated through event bus, shared state, or shared DTOs?
- **Contract impact**: Do the interface signature, parameter types, or return structure change (Breaking Change)?
- **Data impact**: Does it involve database schema changes, cache invalidation, or data migration?

🔗 When GitNexus is available, use `impact` MCP tool for upstream/downstream analysis.

```
Change Impact Analysis Report
─────────────────────────────────────────────
Change target: <module/function name>
Change type: [ ] Behavior modification  [ ] Signature change  [ ] Internal refactor  [ ] Extension enhancement

Direct impact scope:
  - <list modified files/functions>

Indirect impact scope:
  - <list affected callers/dependents>

Is it a Breaking Change: Yes / No
Does it require synchronous changes to other modules: Yes (list) / No
Does it involve data changes: Yes (describe) / No
Risk level: Low / Medium / High
─────────────────────────────────────────────
```

### Step 3: Requirements Refinement — Re-examine Under Architecture Constraints

Don't directly implement after receiving requirements — use the established code context to validate and refine them.

**Questions to confirm:**
- In the current architecture, where is **the most natural implementation point** for the behavioral change?
- Can the requirements be achieved through **extending existing abstraction points**, or must core logic be modified?
- Do the requirements conflict with existing design intent?
- Are the boundary conditions of the requirements clear?

**Core principle: Prioritize finding an "extension-based modification" path; only then consider "invasive modification."**

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

### Step 4: Solution Design — Create Modification Plan and Get Confirmation

> Confirm first when involving public interfaces, cross-module changes, or Breaking Changes.

```
Modification Plan
─────────────────────────────────────────────
Requirement summary: <one-sentence description>
Modification strategy: <Configuration / Extension / Decoration / Local modification / Signature change / Structural reorganization>

Change list:
  1. <File A> - <change description>
  2. <File B> - <change description>

Impact scope: <directly/indirectly affected modules>
Breaking Change: Yes / No
Risk points: <if any>

Confirm execution?
─────────────────────────────────────────────
```

### Step 5: Implement — Follow the Minimal Change Principle

**Execution discipline:**
- **Maintain style consistency**: Naming, indentation, comment language fully consistent with surrounding code
- **No hitchhiking**: Don't "optimize" unrelated code while implementing requirements
- **Changes are traceable**: Format: `# change: <requirement description> - <reason for change>`
- **Backward compatibility**: Prefer compatible approaches (default parameters, overloading, adapters) unless user explicitly states otherwise
- **Incremental implementation**: Do structural adjustments first, then behavioral changes

**Common backward compatibility approaches:**
```python
# ✅ Add optional parameter, old calling style unaffected
def process_order(order_id: str, priority: int = 0):  # priority is newly added
    ...

# ✅ Keep old function as adapter, internally calls new implementation
def get_user(user_id):                    # Old interface, preserved
    return get_user_v2(user_id).to_legacy_format()
```

**❌ Forbidden actions:**
- Modifying public interface signatures without confirmation
- Sneaking in "optimizations" unrelated to the current requirement
- Deleting code that's temporarily unused without informing the user
- Changing return value structures without updating all callers

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

---

## Workflow Tailoring by Task Scale

**Lightweight** (minor single-function logic adjustment, config changes, style fixes):
- Required: Step 5 only
- Optional: Step 1 (quick scan)
- Skip: Steps 2–4, Step 6

**Medium** (modify module internal logic, add/remove internal functions):
- Required: Step 1 → Step 5 → Step 6
- Optional: Step 3
- Skip: Steps 2, 4

**Large** (cross-module changes, public interface modifications, Breaking Changes):
- Required: All 6 steps in order

---

## Common Pitfalls

| Pitfall | Description | Correct Approach |
|---------|-------------|-----------------|
| Act without reading | Modified function without reading callers | At minimum trace one level up |
| Hitchhiking | Smuggled in "opportunistic optimizations" | Strict separation: change only serves the current requirement |
| Implicit Breaking Change | Changed return value structure assuming callers unaffected | Proactively check all callers |
| Over-modification | User requested minor adjustment but entire module was rewritten | Follow minimal change principle |
| Forgot compatibility | Directly changed signature when modifying public interface | Prefer default parameters/overloading |
| Missed sync | Changed code but forgot to update related docs/types/tests | Audit checklist covers sync items |

---

## Reply Format

**Lightweight task** (single-function logic change, config update, style fix): one sentence only.
```
✅ Modified `<function>`: <what changed> using <strategy> (<file>:<line>).
```

**Medium/large task** (cross-file, public interface, or Breaking Change): full block.
```
─── Modification Summary ────────────────────────────────
① Conclusion:         <one sentence: what changed, which strategy was used, and the outcome>
② Changes:            <files / functions modified; callers updated; backward-compat shims added>
③ Risks / Assumptions: <Breaking Change status; compatibility assumptions; callers not yet adapted>
④ Verification:       <Step 6 audit result: Passed ✅ / Issues ⚠️ (details); unit test status>
⑤ Needs your input:   <Breaking Change approval; callers that must still be updated by the user>
────────────────────────────────────────────────────────
```
