# Code Review Checklist

This checklist is **mandatory** for every milestone completion. The assigned engineer must complete this checklist before a milestone can be marked as complete. No item may be skipped — if an item is not applicable, mark it N/A with a brief justification.

This checklist is designed for AI-assisted development and covers the most common issues with AI-generated code in addition to standard engineering quality checks.

---

## How to Use

1. Copy this checklist into the milestone's commit description or into a `REVIEW_MN.md` file (where N is the milestone number) in the `docs/reviews/` folder.
2. Work through each item. Check the box when verified.
3. If any item fails, the milestone **cannot** be marked complete. Fix the issue, rebuild, and re-review.

---

## 1. Definition of Ready (Pre-Implementation)

- [ ] JIRA ticket exists for this milestone with module summary and requirements as description
- [ ] Requirements were signed off on the JIRA ticket before implementation began
- [ ] All implementation was done on the application branch (no direct commits to the default branch)
- [ ] MODULE.md stubs existed for all modules this milestone created or modified **before** implementation began (not created after the fact)
- [ ] MODULE.md stubs contained at minimum: Module Name, Responsibility, and planned Public Interface
- [ ] CLAUDE.md Active Milestone was pointing to this milestone (with JIRA ID) during implementation
- [ ] AI tool was provided project context at session start (CLAUDE.md, milestone details, MODULE.md files, folder structure)

## 2. Build Verification

- [ ] Build command(s) are documented in CLAUDE.md's **Build Validation** section (exact commands, working directory, expected result)
- [ ] Build was executed using the exact method from CLAUDE.md's Build Validation section (by the AI tool if automated, or by the engineer if manual — e.g., VS Code CMake: Build)
- [ ] All target platforms listed in CLAUDE.md have been built (not just one)
- [ ] Build produces zero errors and zero warnings on every target platform
- [ ] Build output artifacts exist at the expected paths documented in CLAUDE.md

## 3. File Structure and Conventions

- [ ] No file exceeds the maximum line limit defined in CLAUDE.md (default: 300 lines)
- [ ] Every file has a single, clear purpose — no mixed responsibilities
- [ ] File and folder names are descriptive (no `utils`, `helpers`, `misc`, `temp`, `stuff`)
- [ ] Folder structure aligns with existing repository/organization conventions
- [ ] No unnecessary files were created (no orphaned scaffolding, empty files, or duplicates)

## 4. Module Organization

- [ ] Related files are grouped into module subfolders where appropriate (3+ related files)
- [ ] Every module subfolder contains a MODULE.md
- [ ] MODULE.md accurately describes the module's current state (not a stale placeholder)
- [ ] Module boundaries are respected — no file reaches into another module's internals

## 5. AI-Generated Code Quality

These items target the top 10 failure modes of AI-generated code:

**Completeness and correctness:**
- [ ] No placeholder or stub code left behind (e.g., `// TODO: implement`, `pass`, `...`, empty function bodies)
- [ ] No dead code — unused functions, unreachable branches, commented-out blocks
- [ ] No hardcoded values that should be configurable (magic numbers, hardcoded paths, embedded credentials)

**Hallucinated and outdated code:**
- [ ] No hallucinated APIs — every function, method, class, and import used actually exists in the dependency versions specified in CLAUDE.md. Verify against official documentation, not assumptions.
- [ ] No deprecated or removed APIs — functions/methods used are current and supported in the pinned dependency versions. Check for deprecation warnings at build time and review any suppressed warnings.
- [ ] No fabricated import paths — every import/include resolves to a real package or module in the project or its dependencies

**Duplication and copy-paste errors:**
- [ ] No duplicate logic — check if similar code already exists elsewhere in the project
- [ ] No copy-paste inconsistencies — when AI reuses a pattern across multiple locations, verify that variable names, constants, string literals, and context-specific values have been correctly updated for each usage (e.g., a copied BLE handler doesn't still reference the wrong characteristic UUID)

**Structure and style:**
- [ ] No overly generic or boilerplate code that doesn't serve the project's actual needs
- [ ] Variable, function, and type names are meaningful and consistent with the project's conventions
- [ ] No unnecessary abstractions — code is as simple as the problem requires

## 6. Functional Correctness

- [ ] The milestone's acceptance criteria (from MILESTONES.md) are fully met
- [ ] Edge cases and error paths have been considered (not just the happy path)
- [ ] External inputs are validated at system boundaries (user input, API responses, file I/O)
- [ ] Resource management is correct — every opened resource is closed (memory alloc/free, file handles, sockets, database connections, timers). Check for missing `finally`/`defer`/cleanup paths.
- [ ] No subtle logic errors — specifically check for: inverted conditions (`>` vs `<`, `==` vs `!=`), off-by-one in loops/arrays, wrong comparison operators, flawed boundary checks. AI-generated logic often *looks* correct but has these silent bugs.
- [ ] State transitions match the documented state model (if applicable) — verify each transition is reachable and leads to the correct next state

## 7. Security (Basic)

- [ ] No credentials, API keys, tokens, or secrets in source code
- [ ] No sensitive data written to logs
- [ ] User/external input is sanitized before use (no injection vulnerabilities)
- [ ] File paths are validated (no path traversal vulnerabilities)
- [ ] Dependencies are from trusted sources and versions are pinned

## 8. Documentation

- [ ] Project README.md is updated to reflect the current state after this milestone
- [ ] MODULE.md files are finalized from stubs into complete documentation (all sections filled — not just name and responsibility)
- [ ] CLAUDE.md active milestone reference is updated to the next milestone (or marked complete)
- [ ] Architecture/data flow diagrams are updated if the system structure changed
- [ ] MILESTONES.md is updated — current milestone marked Complete, next milestone reflects any learnings

## 9. Testing Readiness

*Note: Code review runs before testing. This section verifies that the code is ready to be tested — it does not verify test results. Test results are captured separately in `docs/tests/TEST_MN.md` after the commit is made.*

- [ ] Every signed-off requirement (R1, R2, R3...) from MILESTONES.md is addressable by the implementation — no requirement was missed or left unimplemented
- [ ] Each module's public interface (per MODULE.md) is fully implemented and callable — no stub or placeholder functions remain
- [ ] Code is testable — no hidden dependencies, hardcoded test-bypasses, or conditions that would prevent verification on hardware
- [ ] All acceptance criteria from MILESTONES.md are addressable by the current implementation

## 10. Version Control and JIRA

- [ ] All work was done on the application branch, not the default branch
- [ ] Only milestone-related changes are included in the commit (no unrelated edits)
- [ ] Commit message references both the milestone number and JIRA ID (e.g., `Milestone N [JIRAID]: Title`)
- [ ] No generated artifacts (build outputs, binaries, caches) are committed
- [ ] No sensitive files (.env, credentials, private keys) are committed
- [ ] .gitignore is updated if new file types or build artifacts were introduced
- [ ] JIRA ticket will be transitioned to Done after all gates pass

---

## Sign-Off

| Field                  | Value                                                   |
|------------------------|---------------------------------------------------------|
| **Milestone**          | Milestone N: _title_                                    |
| **JIRA ID**            | _PROJECT-NNN_                                           |
| **Branch**             | Application branch: `_short_app_name_`                  |
| **Reviewed By**        | _name (engineer)_                               |
| **Date**               | _YYYY-MM-DD_                                            |
| **Build Commands Used**| _list each command exactly as run from CLAUDE.md_       |
| **Build Executed By**  | AI Tool / Engineer _(per CLAUDE.md Build Validation method)_ |
| **Build Result**       | Pass / Fail _(per platform)_                            |
| **Test Report**        | `docs/tests/TEST_MN.md` — Pass / Fail                  |
| **All Items Passed**   | Yes / No                                                |
| **JIRA Updated**       | Yes / No                                                |
| **Notes**              | _any exceptions or follow-ups_                          |
