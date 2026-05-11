---
name: tdd-harness-mode
description: Enforce a strict TDD workflow for coding agents, including asking clarification questions before test-case generation when product policy, acceptance criteria, API behavior, UI/browser flow verification, data model, or developer decisions are ambiguous. Use when the user says "TDD harness mode", "TDD 기반으로 작업", "red/green/check/review", asks to create or install an agent TDD harness, or wants vibe-coding/code changes where tests must be written before implementation and verified through executable gates.
---

# TDD Harness Mode

Use this skill to make agentic coding follow a verifiable TDD loop instead of relying on model claims.

## Core Rule

Do not implement production behavior before adding or updating a focused failing test, unless the user explicitly asks to bypass TDD.

Before writing tests, infer the relevant use cases and identify decision points. If a decision affects user-visible behavior, API contracts, security, permissions, data retention, billing, performance budgets, or compatibility, ask the developer concise clarification questions and wait for the answer before continuing.

For detailed UI changes or flows that start in the frontend and continue through state, API, routing, persistence, or permissions, ask whether Playwright/browser-level verification should be included before generating tests, unless the user already specified the verification method.

The required phase order is:

```text
start -> plan -> red -> confirm-red -> green -> check -> review -> done
```

- `plan`: record inferred use cases, decisions, targeted command, and UI/browser verification choice.
- `red`: run the targeted test and expect failure.
- `confirm-red`: confirm the failure is the intended missing behavior, not setup noise.
- `green`: run the same targeted test and expect success.
- `check`: run the full verification suite and expect success.
- `review`: inspect diff, changed tests, logs, and residual risk.

Never claim completion when the full check failed or was not run.

## If The Repo Already Has The Harness

Use the local harness commands:

```bash
./scripts/tdd-cycle start --id <task-id> --spec SPEC.md --reset
./scripts/tdd-cycle doctor
./scripts/tdd-cycle plan --summary "<plan>" --test-command "<focused test command>" --playwright yes|no|not-applicable
./scripts/tdd-cycle red -- ./scripts/test-target <focused test command>
./scripts/tdd-cycle confirm-red --category missing-behavior --reason "<why red is meaningful>"
./scripts/tdd-cycle green -- ./scripts/test-target <same focused test command>
./scripts/tdd-cycle check
./scripts/tdd-cycle review
./scripts/tdd-cycle done
```

Keep `TODO.md` current while working. Use the same targeted command for red and green.

If multiple agents are sharing one worktree, use task-scoped state instead:

```bash
./scripts/tdd-cycle start --id <task-id> --spec SPEC.md --parallel --reset
./scripts/tdd-cycle plan --task <task-id> --summary "<plan>" --test-command "<focused test command>" --playwright yes|no|not-applicable
./scripts/tdd-cycle red --task <task-id> -- ./scripts/test-target <focused test command>
./scripts/tdd-cycle confirm-red --task <task-id> --category missing-behavior --reason "<why red is meaningful>"
./scripts/tdd-cycle green --task <task-id> -- ./scripts/test-target <same focused test command>
./scripts/tdd-cycle check --task <task-id>
./scripts/tdd-cycle review --task <task-id>
./scripts/tdd-cycle done --task <task-id>
```

Task-scoped runs write evidence under `.agent/tasks/<task-id>/` and avoid
colliding with another task's state, logs, or report.

If the repo has an older installed harness and the `tdd-agent-harness` CLI is
available, update conservatively before starting new work:

```bash
tdd-agent-harness update . --dry-run
tdd-agent-harness update .
```

The update command refreshes managed core files such as `scripts/tdd-cycle` and
preserves project-owned files like `AGENTS.md`, `harness.json`, `scripts/check`,
and `scripts/test-target`.

## If The Repo Does Not Have The Harness

The template lives in `assets/tdd-harness-template/`.

Install conservatively:

1. Inspect the repo first: `rg --files`, existing `AGENTS.md`, test framework, package scripts, and existing `scripts/`.
2. Do not overwrite existing user files blindly.
3. Copy missing template files from `assets/tdd-harness-template/`.
4. If `AGENTS.md` already exists, append or merge a short "TDD Harness Mode" section instead of replacing it.
5. If `scripts/check` already exists, keep it and ensure it runs the full verification suite.
6. If `scripts/test-target` already exists, keep it and ensure it can run the focused test command.
7. Ensure `scripts/tdd-cycle`, `scripts/check`, and `scripts/test-target` are executable.
8. Run `./scripts/check` to validate the installed harness.

After installation, use the normal phase order.

## Working A Code Task

When a user asks for a code change under this skill:

1. Read `AGENTS.md`, `SPEC.md` if present, and relevant source/test files.
2. Infer likely use cases, edge cases, and acceptance criteria from the request and codebase.
3. Separate inferred defaults from developer decision points.
4. If any decision point changes the test oracle or public behavior, ask concise questions and stop before editing tests.
5. After the developer answers, update the test plan and identify the smallest focused test that proves the requested behavior.
6. Run the plan gate before editing tests.
   If another agent may be active in the same worktree, start with `--parallel`
   and pass `--task <task-id>` to every later gate.
7. Add or update that test before changing production code.
8. Run the red gate and inspect the failure log. If the failure is syntax, import, fixture, environment noise, timeout, or an incorrect assertion, fix the test/setup and rerun red.
9. Run `confirm-red` only when the failure proves the intended missing behavior.
10. Implement the smallest change to pass the focused test.
11. Run the green gate with the exact same targeted command.
12. Refactor only after green, then rerun the focused test if refactoring changed behavior-sensitive code.
13. Run full check.
14. Run review and report changed files, plan/red/confirm-red/green/check commands, results, and remaining risk.

## Clarification Gate

Ask before test generation when ambiguity changes what "correct" means. Typical blockers:

- limits, thresholds, timeouts, retries, or rate-limit windows;
- authorization, role, tenant, ownership, or privacy behavior;
- API status codes, error messages, response shape, or backwards compatibility;
- persistence, migration, cleanup, idempotency, or concurrency rules;
- billing, quota, audit, notification, or external side effects;
- UI copy, accessibility behavior, empty states, or destructive actions.
- whether detailed UI changes or frontend-originated flows should be verified with Playwright/browser E2E tests.

Do not ask for details that can be discovered from the repo, such as the test runner, existing naming style, or nearby helper APIs. If ambiguity is non-blocking, proceed with a documented assumption and mention it in the final response.

Do not add Playwright or browser-test dependencies without developer approval. If Playwright already exists and the developer wants browser verification, prefer the repo's existing Playwright command and test conventions.

## Choosing Commands

Prefer repo-native commands:

- JavaScript/TypeScript: `pnpm vitest run ...`, `npm test -- ...`, `pnpm test`, `pnpm typecheck`, `pnpm lint`
- Browser/UI flow: after approval, `pnpm playwright test ...`, `npm run test:e2e -- ...`, or the repo's existing browser-test command
- Python: `pytest tests/path.py::test_name`, then `pytest` plus lint/type checks if configured
- Rust: `cargo test test_name`, then `cargo fmt --check`, `cargo clippy --all-targets -- -D warnings`, `cargo test`
- Go: `go test ./path`, then `go test ./...`

If a focused command is ambiguous and cannot be inferred from the repo, ask one concise question before editing.

## Quality Gates

Treat these as blockers:

- Plan gate missing before red.
- Red test unexpectedly passes.
- Red failure is caused by syntax, imports, fixtures, environment setup, timeout, or another non-semantic failure.
- Semantic red confirmation missing before green.
- Green test fails.
- Full check fails.
- The final diff has no test change for a behavior change, unless the user explicitly requested a non-testable maintenance task.
- Tests were deleted, skipped, snapshotted, or weakened to get green.
  Review flags `.skip`, `.only`, assertion reduction, and snapshot churn as warnings.

## Final Response

Keep the final answer short. Include:

- changed files;
- plan gate result;
- red command and result;
- semantic red confirmation;
- green command and result;
- full check result;
- review warnings, including test weakening or risk hints;
- skipped checks or residual risks.
