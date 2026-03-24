---
name: sextant-write-tests
description: Use when writing test cases, adding test coverage, or verifying code behavior through tests. Stronger signals: "write tests", "add tests", "unit test", "integration test", "test coverage", "TDD", "test this function". Also triggered automatically after a bug fix to write the reproduction test. Apply this skill before starting any test-writing work.
---

!`awk 'f;/^---$/{c++}c==2{f=1}' ${CLAUDE_SKILL_DIR}/../principles/SKILL.md`

!`[ -d .gitnexus ] && awk 'f;/^---$/{c++}c==2{f=1}' ${CLAUDE_SKILL_DIR}/../tool-gitnexus/SKILL.md || true`

---

# Test Writing Workflow

## Core Principle

The value of tests is not "line coverage," but **accurately reporting regressions when code changes**. Good tests are a safety net for future refactoring — they go red only when behavior is truly broken, not when unrelated changes are made.

---

## Entering from a Bug Fix

If this test session was triggered by a bug fix, apply the following adjustments before entering the standard workflow:

**1. Write the reproduction test first — before anything else.**

The root cause and trigger conditions are already known from the bug fix. Use that analysis directly:

```python
def test_<bug_description>():
    # This test MUST FAIL before the fix is applied.
    # It documents the exact condition that triggered the bug.
    result = <call using the trigger conditions from the bug fix>
    assert <the correct behavior that was previously broken>
```

**2. Skip Step 1 (code analysis) for the fixed function.** Jump directly to Step 2, using the impact assessment from the bug fix as input for "what callers depend on."

**3. Prioritize boundary tests adjacent to the bug.** Focus on the boundary conditions the bug exposed — null, zero, extreme values, race conditions.

**4. Name the reproduction test clearly:**

```python
def test_calculate_discount_zero_rate_does_not_divide_by_zero():
    # fix: rate=0 caused ZeroDivisionError (see bug fix root cause)
    assert calculate_discount(price=100, rate=0) == 100
```

Once the reproduction test is in place and passing, skip to Step 2 for any additional coverage.

**If the reproduction test still fails after the fix was applied:** stop the test-writing workflow. Report to the user: "The reproduction test is still failing — the fix may be incomplete. Returning to `sextant-fix-bug` to re-evaluate the root cause." Do not proceed to Step 2.

---

## Before You Start

### Five Characteristics of Good Tests (F.I.R.S.T)

| Characteristic | Description |
|---------------|-------------|
| **Fast** | Single test < 100ms, full test suite < 30s |
| **Independent** | No dependencies between tests, no dependency on execution order |
| **Repeatable** | Results consistent across any environment; no dependency on external services, system time, or random numbers |
| **Self-validating** | Results are pass/fail; no manual log inspection required |
| **Prioritized by Impact** | Write tests for high-impact functions first: core business logic, functions with many callers, code that is hard to debug manually |

### Choosing the Test Level

```
Test Pyramid (bottom to top: decreasing quantity, increasing cost)
─────────────────────────────────────────────
        ╱ ╲           E2E Tests — few, verify key user paths
       ╱   ╲
      ╱─────╲         Integration Tests — moderate, verify inter-module collaboration
     ╱       ╲
    ╱─────────╲       Unit Tests — many, verify behavior of individual functions/classes
─────────────────────────────────────────────
```

**Selection criteria:**
- Pure functions, computation logic, data transformation → **Unit tests**
- Inter-module interaction, database reads/writes, API calls → **Integration tests**
- Complete user operation flows → **E2E tests** (cover core paths only)

---

## Complete Execution Workflow

### Step 1: Analyze the Code Under Test

Before writing tests, thoroughly understand the behavioral contract of the code under test.

**Questions to answer:**
- What is the **responsibility** of the function/class under test?
- What are its **inputs**? What is the **valid range** and **boundary values** for each input?
- What are its **outputs** (return values + side effects)?
- What **preconditions** does it have?
- Which **exceptions** might it throw? Under what conditions?
- Which **external collaborators** does it depend on? Do these need to be mocked?

🔗 When GitNexus is available, use `context` MCP tool to get callees (external dependencies) automatically.

### Step 2: Design Test Boundaries

Divide the behavioral space into discrete test regions.

**Three required test scenarios:**

**① Happy Path** — typical input → expected output; each meaningful parameter combination

**② Boundary Conditions:**
- Null/zero/empty collection/empty string
- Maximum/minimum/just beyond range
- Single-element collection (off-by-one happens most here)
- Type boundaries (integer overflow, float precision)

**③ Error Path:**
- Invalid input → expected exception/error code
- External dependency failure → expected degradation/error handling
- Concurrency/race conditions (if applicable)
- Timeout scenarios (if network/IO is involved)

```
Test Boundary Matrix
─────────────────────────────────────────────────────
Target under test: <function/class name>

Happy path:
  case_1: <input description> → <expected output>

Boundary conditions:
  boundary_1: <boundary input> → <expected behavior>

Error path:
  error_1: <invalid input> → <expected exception/error>
─────────────────────────────────────────────────────
```

### Step 3: Determine Test Structure

**Naming conventions:** Test names must describe behavior, not repeat the function name.

```python
# ✅ Good test naming
def test_discount_returns_zero_when_rate_exceeds_price():
def test_login_fails_with_expired_token():
def test_parse_handles_empty_input_gracefully():

# ❌ Poor test naming
def test_discount():
def test_login():
```

**Naming pattern:** `test_<behavior>_<condition>` or `test_<behavior>_when_<condition>_then_<expectation>`

**AAA Structure (Arrange → Act → Assert):**

```python
def test_order_total_applies_discount_for_vip_user():
    # Arrange
    user = create_vip_user()
    items = [Item("book", price=100), Item("pen", price=20)]
    order = Order(user=user, items=items)

    # Act
    total = order.calculate_total()

    # Assert
    assert total == 96.0  # VIP 20% discount: (100 + 20) * 0.8
```

**Each test verifies only one behavior.** Multiple asserts checking different aspects of the same behavior are acceptable.

### Step 4: Handle External Dependencies

| Dependency Type | Isolation Method | Use Case |
|----------------|-----------------|----------|
| Pure interface dependency (Repository, Client) | Mock objects | Unit tests |
| Database | In-memory database / test containers | Integration tests |
| External API | HTTP mock (e.g., responses, wiremock) | Integration tests |
| File system | Temp directory + teardown cleanup | File read/write logic |
| Time/random | Inject controllable clock / fixed seed | Deterministic results needed |

**Mock discipline:**
- Mocked behavior must be consistent with the real implementation's contract
- Don't mock internal implementations of code you don't own — mock interfaces
- If mock setup is more complex than the code under test, the code has too heavy dependencies

🔗 When GitNexus is available, use `context` callees to distinguish internal vs external dependencies.

### Step 5: Implement Tests

**Recommended implementation order:**
1. Write the most typical happy path case first — verify AAA structure and mock setup are correct
2. Add boundary conditions — cover boundary items in the Step 2 matrix one by one
3. Write error paths — verify error handling meets expectations

**Reference existing test style:** New tests' file organization, naming style, assertion library, and fixture patterns must be consistent with existing tests in the project.

🔗 When GitNexus is available, use `query "<function name> test"` to find reference tests.

### Step 6: Validate Test Quality

```
Test Quality Checklist
─────────────────────────────────────────────────────
[ ] Independence: No dependencies between tests? Can run in any order? Can run individually?
[ ] Determinism: No dependency on system time, random numbers, external services?
[ ] Readability: Does reading the test name tell you what's being tested? Is AAA structure clear?
[ ] Validity: If a line of logic in the code under test is deleted, will the test fail?
[ ] Non-brittleness: Does the test depend on implementation details rather than behavior?
[ ] Boundary coverage: Does each case in the Step 2 matrix have a corresponding test?
[ ] Error messages: Is the error message on assertion failure sufficient to locate the problem?
[ ] Speed: Is a single test < 100ms?
─────────────────────────────────────────────────────
```

**"Validity" check technique (mutation testing mindset):**
Make these changes to the code under test; check if tests fail:
- Change `>` to `>=`
- Change return value to `None` / `null`
- Comment out a key conditional branch

If tests still pass, they cover lines but don't verify behavior.

---

## Forbidden Actions

- **Write business logic in tests**: Directly assert expected concrete values; don't replicate computation logic
- **Assert `assertTrue(result is not None)`**: Doesn't verify any behavior
- **Depend on execution order**: Each test must be self-contained
- **Test private methods**: Test behavior of public interfaces, not implementation details
- **Ignore flaky tests**: Fix or delete them — flaky tests cause teams to ignore all failures

---

## Reply Format

**Lightweight task** (1–3 tests for a single function): one sentence only.
```
✅ Added <N> tests for `<function>` covering <scenarios> (<test_file>:<line>).
```

**Medium/large task** (new test module, full coverage pass, or post-bug-fix reproduction tests): full block.
```
─── Test Summary ────────────────────────────────────────
① Conclusion:         <one sentence: N tests written for [target], covering [happy/boundary/error paths]>
② Changes:            <test files / functions added or modified, with scenario count per category>
③ Risks / Assumptions: <mock contracts assumed; known coverage gaps; scenarios deferred>
④ Verification:       <Step 6 quality checklist result; all tests passing / not yet run>
⑤ Needs your input:   <behavioral contracts that are ambiguous; tests the user should execute to confirm>
────────────────────────────────────────────────────────
```
