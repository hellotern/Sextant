# Test Writing Workflow

> This file is loaded on demand by the `coding-principles` Skill when a test writing task is identified. General coding principles (SOLID, DRY, baseline rules, etc.) are in the main SKILL.md and are not repeated here.

---

## Core Principle

The value of tests is not "line coverage," but **accurately reporting regressions when code changes**. Good tests are a safety net for future refactoring — they go red only when behavior is truly broken, not when unrelated changes are made.

---

## Entering from a Bug Fix

If this test session was triggered by a bug fix workflow (`fix-bug.md`), the starting context is different from a clean test-writing task. Apply the following adjustments before entering the standard workflow:

**1. Write the reproduction test first — before anything else.**

The root cause and trigger conditions are already known from fix-bug Step 1. Use that analysis directly:

```python
def test_<bug_description>():
    # This test MUST FAIL before the fix is applied.
    # It documents the exact condition that triggered the bug.
    result = <call using the trigger conditions from fix-bug Step 1>
    assert <the correct behavior that was previously broken>
```

This test is the proof that the fix works. Commit it alongside the fix.

**2. Skip Step 1 (code analysis) for the fixed function.**

The behavioral contract analysis is already done. Jump directly to Step 2 (test boundary design), using the impact assessment from fix-bug Step 2 as the input for "what callers depend on."

**3. Prioritize boundary tests adjacent to the bug.**

After the reproduction test, focus on the boundary conditions that the bug exposed — null, zero, extreme values, race conditions — rather than general coverage. These are the scenarios most likely to regress.

**4. Name and document the reproduction test clearly.**

The test name and a one-line comment should reference the specific bug condition so future developers understand why this case exists:

```python
def test_calculate_discount_zero_rate_does_not_divide_by_zero():
    # fix: rate=0 caused ZeroDivisionError (see fix-bug Step 1 root cause)
    assert calculate_discount(price=100, rate=0) == 100
```

Once the reproduction test is in place and passing, **skip to Step 2 (Design Test Boundaries)** for any additional coverage. Step 1 (code analysis) is already complete — the root cause and behavioral contract were established in fix-bug.

---

## Before You Start

### Five Characteristics of Good Tests (F.I.R.S.T)

| Characteristic | Description |
|---------------|-------------|
| **Fast** | Single test < 100ms, full test suite < 30s; slow tests won't be run frequently |
| **Independent** | No dependencies between tests, no dependency on execution order, each test can run alone |
| **Repeatable** | Results are consistent across any environment; no dependency on external services, system time, or random numbers |
| **Self-validating** | Test results are pass/fail; no manual log inspection required |
| **Prioritized by Impact** | Write tests for high-impact functions first: core business logic, functions with many callers, and code that is hard to debug manually. In AI-assisted workflows, timing is controlled by the user; focus on coverage quality by impact rather than by when tests are written. |

### Choosing the Test Level

```
Test Pyramid (bottom to top: decreasing quantity, increasing cost)
─────────────────────────────────────────────
        ╱ ╲           E2E Tests
       ╱   ╲          Few, verify key user paths
      ╱─────╲
     ╱       ╲        Integration Tests
    ╱         ╲       Moderate, verify inter-module collaboration
   ╱───────────╲
  ╱             ╲     Unit Tests
 ╱               ╲    Many, verify behavior of individual functions/classes
╱─────────────────╲
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
- What is the **responsibility** of the function/class under test? (One-sentence description)
- What are its **inputs**? What is the **valid range** and **boundary values** for each input?
- What are its **outputs** (return values + side effects)?
- What **preconditions** does it have (state that must be satisfied before calling)?
- Which **exceptions** might it throw? Under what conditions?
- Which **external collaborators** does it depend on (other modules, databases, APIs)? Do these need to be mocked or instantiated?

**🔗 GitNexus Enhanced — Quickly build a profile of the code under test:**

```
# 1. Get full context of the symbol under test
context({ symbol: "<function/class name under test>" })
# Returns: callers (who uses it), callees (what it uses), inheritance, execution processes
# Key info: callees list is the candidate mock list for collaborators

# 2. View the complete execution flow the function participates in (understand its role in the system)
trace({ symbol: "<function name under test>" })
# Helps understand: in what scenarios is this function called, where does input come from, where does output go

# 3. Find existing test files in the project (as style and organization reference)
query({ query: "<module name under test> test spec" })
# Find existing tests as reference to ensure new tests match existing style, naming, and organization
```

**Extract test design information from `context` results:**
- **callers**: How callers use this function reveals its "real interface contract" — test it the way callers call it
- **callees**: List of called functions = mock object candidate list. Assess whether each dependency should be mocked or real-instantiated
- **processes**: The execution processes this function belongs to reveal its role in the system, helping identify integration test scenarios

### Step 2: Design Test Boundaries

Divide the behavioral space of the code under test into discrete test regions.

**Three required test scenarios:**

**① Happy Path**
- Typical input → expected output
- Each meaningful parameter combination

**② Boundary Conditions**
- Null/zero/empty collection/empty string
- Maximum/minimum/just beyond range
- Single-element collection (off-by-one happens most here)
- Type boundaries (integer overflow, float precision)

**③ Error Path**
- Invalid input → expected exception/error code
- External dependency failure → expected degradation/error handling
- Concurrency/race conditions (if applicable)
- Timeout scenarios (if network/IO is involved)

**Test boundary matrix template:**

```
Test Boundary Matrix
─────────────────────────────────────────────────────
Target under test: <function/class name>

Happy path:
  case_1: <input description> → <expected output>
  case_2: <input description> → <expected output>

Boundary conditions:
  boundary_1: <boundary input> → <expected behavior>
  boundary_2: <boundary input> → <expected behavior>

Error path:
  error_1: <invalid input> → <expected exception/error>
  error_2: <dependency failure> → <expected degradation behavior>
─────────────────────────────────────────────────────
```

**🔗 GitNexus Enhanced — Assist in discovering boundary scenarios:**

```
# View how callers use the function under test, extract test cases from real usage scenarios
context({ symbol: "<function name under test>" })
# Caller parameter patterns reveal "values that might actually be passed in" — add to happy path

# View upstream impact of the function under test, find scenarios where changes cause regressions
impact({ target: "<function name under test>", direction: "upstream" })
# High-frequency caller scenarios should be prioritized because regressions have the largest impact
```

### Step 3: Determine Test Structure

**Naming conventions:** Test names must describe behavior, not repeat the function name.

```python
# ✅ Good test naming — reading the name tells you what's being tested
def test_discount_returns_zero_when_rate_exceeds_price():
def test_login_fails_with_expired_token():
def test_parse_handles_empty_input_gracefully():

# ❌ Poor test naming — reading the name tells you nothing
def test_discount():
def test_login():
def test_parse_1():
```

**Naming pattern:** `test_<behavior>_<condition/scenario>` or `test_<behavior>_when_<condition>_then_<expectation>`

**AAA Structure (Arrange → Act → Assert):**

```python
def test_order_total_applies_discount_for_vip_user():
    # Arrange — set up test preconditions
    user = create_vip_user()
    items = [Item("book", price=100), Item("pen", price=20)]
    order = Order(user=user, items=items)

    # Act — execute the behavior under test
    total = order.calculate_total()

    # Assert — verify the result
    assert total == 96.0  # VIP 20% discount: (100 + 20) * 0.8
```

**Each test verifies only one behavior.** If a test has multiple unrelated asserts, it should be split into multiple tests. Multiple asserts checking different aspects of the same behavior (e.g., different fields of a return value) are acceptable.

### Step 4: Handle External Dependencies

External dependencies of the code under test (databases, APIs, file systems, other modules) need to be isolated, otherwise tests don't satisfy the Independent and Repeatable requirements.

**Dependency isolation strategies:**

| Dependency Type | Isolation Method | Use Case |
|----------------|-----------------|----------|
| Pure interface dependency (Repository, Client) | Mock objects | Unit tests, only care about the logic of the code under test |
| Database | In-memory database / test containers | Integration tests, need to verify SQL/query logic |
| External API | HTTP mock (e.g., responses, wiremock) | Integration tests, need to verify serialization/error handling |
| File system | Temp directory + teardown cleanup | Testing file read/write logic |
| Time/random | Inject controllable clock / fixed seed | When deterministic results are needed |

**🔗 GitNexus Enhanced — Quickly identify dependencies that need to be mocked:**

```
# callees returned by context are the dependency list of the function under test
context({ symbol: "<function name under test>" })
# Assess each item:
#   - Utility functions from the same module → usually don't need mocking
#   - Service / Repository from other modules → need mocking
#   - External library calls (HTTP, DB) → need mocking or test containers
```

**Mock discipline:**
- Mocked behavior must be consistent with the real implementation's contract — mock return data structures and exception types must be correct
- Don't mock internal implementations of code you don't own — mock interfaces, not concrete classes
- If the mock setup is more complex than the code under test, the code under test has too heavy dependencies; consider refactoring

### Step 5: Implement Tests

> ⚠️ **The baseline rules in SKILL.md also apply to test code** — accurate naming, no magic values, no swallowed exceptions. Tests are code, not second-class citizens.

**Recommended implementation order:**
1. Write the most typical happy path case first — verify AAA structure and mock setup are correct
2. Then add boundary conditions — cover boundary items in the Step 2 matrix one by one
3. Finally write error paths — verify error handling meets expectations

**Reference existing test style:** New tests' file organization, naming style, assertion library, and fixture patterns must be consistent with existing tests in the project. If the project uses pytest, don't introduce unittest; if the project uses describe/it, don't use test_ prefix.

**🔗 GitNexus Enhanced — Find reference tests:**

```
# Find test files for the most similar module to the one under test, as style reference
query({ query: "<module name under test> test" })
```

### Step 6: Validate Test Quality

After writing tests, validate the quality of the tests themselves — bad tests are more dangerous than no tests (they give a false sense of security).

```
Test Quality Checklist
─────────────────────────────────────────────────────
[ ] Independence: No dependencies between tests? Can run in any order? Can run individually?
[ ] Determinism: No dependency on system time, random numbers, external services? Consistent results across multiple runs?
[ ] Readability: Does reading the test name tell you what's being tested? Is AAA structure clear? No unnecessary setup?
[ ] Validity: If a line of logic in the code under test is deleted, will the test fail?
    (If the test still passes after deleting code, it's not truly verifying behavior)
[ ] Non-brittleness: Does the test depend on implementation details rather than behavior?
    (Tests should not go red when internal refactoring doesn't change behavior)
[ ] Boundary coverage: Does each case in the Step 2 matrix have a corresponding test?
[ ] Error messages: Is the error message on assertion failure sufficient to locate the problem?
[ ] Speed: Is a single test < 100ms? Are there slow dependencies that could be replaced with mocks?
─────────────────────────────────────────────────────
```

**"Validity" check technique (mutation testing mindset):**
Make the following changes to the code under test, check if tests fail:
- Change `>` to `>=`
- Change return value to `None` / `null`
- Comment out a key conditional branch
- Swap the order of two parameters

If the tests still pass after these changes, the tests are "self-deceiving" — they cover code lines but don't verify behavior.

---

## Testing Strategies by Task Type

### Writing Tests for Existing Code

First write "characterization tests" for existing behavior to pin down current behavior:
1. Call the function, capture the current return value
2. Write the captured return value as an assert
3. This is not an assertion of "correct behavior," but a snapshot of "current behavior" — any deviation during subsequent refactoring will be caught

### Writing Tests for Bug Fixes

First write a **failing test that reproduces the bug**, then fix the code to make it pass:
```python
def test_discount_does_not_divide_by_zero_when_rate_is_zero():
    # This test should FAIL before the fix
    result = calculate_discount(price=100, rate=0)
    assert result == 100  # Should PASS after the fix
```

### Writing Tests for New Features

Write alongside the code. If using TDD, the order is: write test → see it fail → write minimal implementation → see it pass → refactor. TDD is not mandatory, but tests must be committed together with the feature code.

---

## Forbidden Actions

- **Write business logic in tests**: Tests should not replicate the computation logic of the code under test to verify it — directly assert expected concrete values
- **Assert `assertTrue(result is not None)`**: This doesn't verify any behavior and almost never fails
- **Depend on execution order**: State set up by test_A consumed by test_B — each test must be self-contained
- **Test private methods**: Test the behavior of public interfaces, not implementation details
- **Ignore flaky tests**: If a test fails intermittently, either fix it or delete it — flaky tests cause teams to ignore all failures

---

## Common Pitfalls

| Pitfall | Manifestation | Correct Approach | 🔗 GitNexus Assistance |
|---------|--------------|-----------------|------------------------|
| Testing implementation | asserting internal variable values rather than public interface output | Test behavior not implementation; internal refactoring should not cause tests to go red | — |
| Over-mocking | All dependencies mocked; tests only verify the mocks themselves | Only mock external dependencies; keep same-module utility functions real | `context` callees to distinguish internal/external dependencies |
| Incomplete testing | Only tested happy path, ignored boundaries and errors | Strictly cover three scenario types per Step 2 matrix | `impact upstream` to find high-frequency call scenarios |
| Style inconsistency | New tests naming/organization inconsistent with existing tests | Find reference tests first, strictly imitate existing style | `query` to search existing test files |
| Slow tests | Real database/network integrated; single test runs for seconds | Use mocks for unit tests, separate integration tests | — |
| Brittle assertions | Assertions contain timestamps, random IDs, or other non-deterministic values | Only assert deterministic fields; ignore non-deterministic ones | — |

---

## Reply Format

End every test-writing response with this block (omit a field only if it genuinely has nothing to report):

```
─── Test Summary ────────────────────────────────────────
① Conclusion:         <one sentence: N tests written for [target], covering [happy/boundary/error paths]>
② Changes:            <test files / functions added or modified, with scenario count per category>
③ Risks / Assumptions: <mock contracts assumed; known coverage gaps; scenarios deferred>
④ Verification:       <Step 6 quality checklist result; all tests passing / not yet run>
⑤ Needs your input:   <behavioral contracts that are ambiguous; tests the user should execute to confirm>
────────────────────────────────────────────────────────
```
