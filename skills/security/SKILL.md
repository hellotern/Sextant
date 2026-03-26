---
name: sextant-security
description: Use for a security-focused audit of code changes or modules. Stronger signals: "security review", "check for vulnerabilities", "is this safe", "audit this", "OWASP", "injection", "auth check", "XSS", "SQL injection". Distinct from sextant-review-code (general quality review); this skill specifically targets security dimensions. Can be run standalone or as a follow-up after sextant-review-code.
---

!`python3 ${CLAUDE_SKILL_DIR}/../bin/strip_frontmatter.py ${CLAUDE_SKILL_DIR}/../principles/SKILL.md`

!`python3 ${CLAUDE_SKILL_DIR}/../bin/strip_frontmatter.py ${CLAUDE_SKILL_DIR}/../tool-gitnexus/SKILL.md --if-dir-exists .gitnexus`

---

# Security Audit Workflow

## Core Principle

Security vulnerabilities are architectural violations in disguise: injection attacks are layer violations (untrusted data reaching logic without sanitization at the entry boundary); privilege escalation is an SRP violation (authorization logic entangled with business logic); secret leakage is a hidden dependency violation (credentials embedded in code rather than injected from outside). Fixing the architecture fixes the vulnerability.

> **Limitation declaration:** This skill performs static code pattern analysis. It cannot execute `npm audit`, `pip-audit`, `bandit`, `semgrep`, `trivy`, or any other automated scanner. The dependency findings in Dimension 4 are a preliminary review — they do not substitute for running real tooling.

---

## Audit Dimensions

### Dimension 1: Input Validation

**Scope:** All public interfaces, API endpoints, and externally-controlled input paths.

| Check | Pass condition |
|-------|---------------|
| Entry-layer validation | All external parameters (request body, query string, headers, file uploads) are validated before entering the logic layer |
| SQL parameterization | SQL is built with parameterized queries / prepared statements — never string concatenation |
| HTML output escaping | All user-controlled data is escaped before rendering in HTML (XSS prevention) |
| Shell command safety | Shell invocations use argument arrays, not string interpolation of user input |
| Path canonicalization | File paths are resolved (`os.path.realpath()` / `.resolve()`) before use to prevent path traversal |

```
Input Validation Findings
─────────────────────────────────────────────
Interface / endpoint: <name>
  [ ] Validated at entry layer before logic layer
  [ ] SQL parameterized (no string concatenation)
  [ ] HTML output escaped
  [ ] Shell commands use argument arrays
  [ ] File paths canonicalized
  Gaps: <list any failing checks>
─────────────────────────────────────────────
```

### Dimension 2: Authentication and Authorization

**Scope:** All access-controlled endpoints, operations, and data reads/writes.

| Check | Pass condition |
|-------|---------------|
| AuthN at entry layer | Authentication checks are performed at the entry layer (route handler / controller) — not inside the logic layer |
| AuthZ at entry layer | Authorization checks are performed at the entry layer alongside authentication |
| Both checked | Both authentication (who are you?) AND authorization (are you allowed to do this?) are verified — not just one |
| No bypass path | No path to protected resources exists that skips the auth check (e.g., internal endpoint, direct service call) |
| Tokens out of logs | Session tokens, JWTs, and auth credentials are excluded from application logs |
| Tenant isolation | For multi-tenant systems: tenant isolation is enforced at the data query level, not only in the UI |

```
Auth Findings
─────────────────────────────────────────────
Endpoint / operation: <name>
  [ ] AuthN check at entry layer
  [ ] AuthZ check at entry layer
  [ ] Both AuthN and AuthZ verified
  [ ] No bypass path identified
  [ ] Session / auth tokens excluded from logs
  [ ] Tenant isolation enforced (if applicable)
  Gaps: <list any failing checks>
─────────────────────────────────────────────
```

### Dimension 3: Sensitive Data Handling

**Scope:** All data storage, transmission, logging, and serialization paths.

| Check | Pass condition |
|-------|---------------|
| No hardcoded credentials | No literal credential values assigned to variables matching: `password`, `api_key`, `secret`, `token`, `private_key`, `access_key` (case-insensitive) |
| PII out of logs | Personally identifiable information (names, emails, phone numbers, national IDs) is not written to logs |
| Sanitized error messages | Error messages returned to external callers do not expose stack traces, file paths, SQL queries, or internal structure |
| Response field masking | Sensitive fields (passwords, tokens, PII) are stripped or masked from API response objects before serialization |
| Secrets from environment | Secrets are loaded from environment variables or a secrets manager — not from committed config files |

```
Sensitive Data Findings
─────────────────────────────────────────────
  [ ] No hardcoded credentials (password/key/secret/token literals)
  [ ] PII excluded from logs
  [ ] Error messages sanitized for external callers
  [ ] Sensitive fields stripped from API responses
  [ ] Secrets sourced from env vars / secrets manager (not committed config)
  Gaps: <list any failing checks>
─────────────────────────────────────────────
```

### Dimension 4: Dependency Review

**Scope:** Dependency manifest files (`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`, `pyproject.toml`).

> **Scope boundary:** Claude cannot query live CVE databases or confirm current compromise status of packages. This dimension covers checks that can be performed reliably from the manifest file alone. For vulnerability scanning, authoritative tooling is required (see note below).

| Check | Pass condition |
|-------|---------------|
| Exact version pinning | All production dependencies use exact versions — no `^`, `~`, `*`, or `latest` ranges; floating ranges in production create non-reproducible builds |
| Lock file committed | A lock file exists and is committed: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`, `go.sum` |
| Dev/prod separation | Dev tools, test frameworks, and linters are in `devDependencies` / `[dev-dependencies]` — not in production dependencies |
| No self-referential or phantom imports | No dependencies listed that are not used by the codebase, and no imports used in code that are absent from the manifest |

> **Authoritative scan required:** Run `npm audit`, `pip-audit`, `cargo audit`, or `trivy` to check for known CVEs and supply-chain issues. Claude cannot execute these tools and cannot reliably identify compromised or vulnerable packages from the manifest text alone.

```
Dependency Review Findings
─────────────────────────────────────────────
  [ ] Production dependencies use exact version pinning (no ^ ~ * latest)
  [ ] Lock file exists and is committed
  [ ] Dev dependencies correctly separated from production dependencies
  [ ] No unused or phantom dependencies found
  Gaps: <list any failing checks>
  ⚠️ Authoritative scan required: run npm audit / pip-audit / cargo audit / trivy
─────────────────────────────────────────────
```

---

## Finding Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **CRITICAL** | Directly exploitable with no prerequisites (SQL injection, auth bypass, hardcoded admin credential) | Block merge; fix immediately |
| **HIGH** | Exploitable under specific but realistic conditions (missing auth on an endpoint reachable with a valid session) | Fix before shipping |
| **MEDIUM** | Defense-in-depth gap (error message leaks stack trace, no direct exploit path) | Fix in near-term follow-up |
| **LOW** | Best-practice gap with no current exploit path (PII in debug logs, dev dependency in prod bundle) | Track as tech debt |

---

## Forbidden Actions

- Do not run shell commands, execute scanners, or call external APIs
- Do not mark a finding as "not a vulnerability" because "this code isn't reachable in production" without tracing the actual call path — reachability must be verified, not assumed
- Do not skip Dimension 2 for "internal-only" endpoints — network perimeters can be breached; internal endpoints without auth checks are still vulnerabilities

---

## Reply Format

```
─── Security Audit Summary ──────────────────────────
① Scope:          <files / endpoints / modules reviewed>
② Findings:
   CRITICAL: <count> — <brief list or "none">
   HIGH:     <count> — <brief list or "none">
   MEDIUM:   <count> — <brief list or "none">
   LOW:      <count> — <brief list or "none">
③ Dimension status:
   Input validation:  ✅ clean / ⚠️ N gaps found
   Auth / AuthZ:      ✅ clean / ⚠️ N gaps found
   Sensitive data:    ✅ clean / ⚠️ N gaps found
   Dependencies:      ✅ clean / ⚠️ N concerns — authoritative scan still required
④ Needs your input: <CRITICAL / HIGH items requiring immediate decision before merge>
─────────────────────────────────────────────────────
```
