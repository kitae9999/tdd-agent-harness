# Agent Rules

These rules apply to every coding agent working in this repository.

## Mission

Use test-driven development. The expected output is not just working code, but a
traceable red/green/check cycle with logs and a final report.

## Required Workflow

1. Read `SPEC.md`, `TODO.md`, and the relevant source/test files before editing.
2. Infer likely use cases, edge cases, and acceptance criteria from the request
   and current codebase.
3. Identify developer decision points before writing tests. If ambiguity changes
   what "correct" means, ask concise clarification questions and wait for the
   answer before continuing.
4. Record the plan gate with `./scripts/tdd-cycle plan --summary ... --test-command ... --playwright ...`.
5. Update `TODO.md` with the concrete test plan, implementation plan, assumptions,
   and resolved decisions.
6. Add or update a focused test before changing production code.
7. Run the red gate with `./scripts/tdd-cycle red -- <targeted test command>`.
8. Confirm semantic red with `./scripts/tdd-cycle confirm-red --category <category> --reason <reason>`.
9. Confirm the failure is caused by the intended missing behavior, not by syntax,
   bad fixtures, broken imports, environment setup, or an incorrect assertion.
10. Implement the smallest production change that can make the focused test pass.
11. Run the green gate with `./scripts/tdd-cycle green -- <targeted test command>`.
12. Refactor only after green, and rerun the focused test after refactoring.
13. Run `./scripts/tdd-cycle check` before claiming completion.
14. Run `./scripts/tdd-cycle review` and inspect the final diff.

## Clarification Gate

Ask the developer before generating tests when a decision affects user-visible
behavior, API contracts, security, permissions, data model, billing, side
effects, performance budgets, or backwards compatibility.

For detailed UI changes or flows that start in the frontend and continue through
state, API, routing, persistence, or permissions, ask whether Playwright/browser
verification should be included before generating tests, unless the developer
already specified the verification method.

Typical blockers:

- limits, thresholds, timeouts, retries, or rate-limit windows;
- authorization, role, tenant, ownership, or privacy behavior;
- API status codes, error messages, response shape, or compatibility;
- persistence, migration, cleanup, idempotency, or concurrency rules;
- billing, quota, audit, notification, or external side effects;
- UI copy, accessibility behavior, empty states, or destructive actions.
- whether detailed UI changes or frontend-originated flows should be verified
  with Playwright/browser E2E tests.

Do not ask for details that can be discovered from the repository, such as the
test runner, existing naming style, or nearby helper APIs. If ambiguity is
non-blocking, proceed with a documented assumption and include it in the final
report.

Do not add Playwright or browser-test dependencies without developer approval. If
Playwright already exists and the developer wants browser verification, prefer
the repository's existing Playwright command and test conventions.

Record the final decision with `./scripts/tdd-cycle ui-decision --playwright yes|no|not-applicable`.

## Forbidden Shortcuts

- Do not implement production behavior before proving a failing test, unless the
  user explicitly asks to bypass TDD.
- Do not run red before a passing plan gate.
- Do not run green before semantic red is confirmed.
- Do not delete, skip, loosen, or snapshot-away tests to get green.
- Do not mark the task done after only a targeted test; full check is required.
- Do not hide failing logs. Summarize the failure and fix the root cause.
- Do not make broad refactors unrelated to the spec.
- Do not touch secrets, production credentials, production databases, or deploy
  settings without explicit approval.

## Test Quality Bar

Tests should verify behavior that matters to users or callers. Prefer a narrow
test that fails for the missing behavior and passes after the minimal fix.

Acceptable tests:

- API contract or handler tests for backend behavior.
- Component interaction tests for UI behavior.
- Playwright/browser E2E tests for approved detailed UI or frontend-originated
  flow verification.
- Unit tests around pure domain logic.
- Regression tests that would have caught the bug.

Weak tests:

- Tests that only assert implementation details.
- Snapshot-only tests for new behavior.
- Tests that pass before the fix.
- Tests that require network services unless the spec explicitly requires them.

## Completion Criteria

Before final response, provide:

- changed files;
- plan gate result;
- red gate command and result;
- semantic red confirmation;
- green gate command and result;
- full check command and result;
- any remaining risks or skipped checks.

The final answer must not claim success when `./scripts/tdd-cycle check` failed
or was not run.
