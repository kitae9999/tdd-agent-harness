# Agent Rules

These rules apply to coding agents working in this repository.

## TDD Harness Mode

TDD Harness Mode is available in this repo only when the developer explicitly asks for it.

Explicit triggers include:

- "TDD harness mode"
- "TDD로 구현"
- "TDD 기반으로 작업"
- "red/green/check/review로 진행"
- direct use of the `tdd-harness-mode` skill

For ordinary coding requests, follow the repo's normal instructions and do not
force the TDD harness workflow.

## When TDD Harness Mode Is Explicitly Requested

Use the task-local harness workflow:

```bash
./scripts/tdd-cycle start --id <task-id> --reset
./scripts/tdd-cycle paths --task <task-id>
./scripts/tdd-cycle plan --task <task-id> --summary ... --test-command ... --playwright ...
./scripts/tdd-cycle red --task <task-id> -- <targeted test command>
./scripts/tdd-cycle confirm-red --task <task-id> --category <category> --reason <reason>
./scripts/tdd-cycle green --task <task-id> -- <same targeted test command>
./scripts/tdd-cycle check --task <task-id>
./scripts/tdd-cycle review --task <task-id>
./scripts/tdd-cycle done --task <task-id>
```

Each task writes its active documents and evidence under:

```text
.agent/tasks/<task-id>/SPEC.md
.agent/tasks/<task-id>/TODO.md
.agent/tasks/<task-id>/state.json
.agent/tasks/<task-id>/logs/
.agent/tasks/<task-id>/report.md
```

Root `SPEC.md` and `TODO.md` are templates. In TDD Harness Mode, read and update
the task-local `SPEC.md` and `TODO.md` shown by `./scripts/tdd-cycle paths`, not
the root templates.

## Required TDD Sequence

When TDD Harness Mode is active:

1. Infer likely use cases, edge cases, and acceptance criteria from the request
   and current codebase.
2. Ask concise clarification questions before writing tests when ambiguity
   changes what "correct" means.
3. For detailed UI changes or frontend-originated flows, ask whether
   Playwright/browser verification should be included.
4. Record the plan gate before editing tests.
5. Add or update a focused failing test before changing production code.
6. Run the red gate and confirm the failure is caused by the intended missing
   behavior, not syntax, imports, fixtures, environment setup, or bad assertions.
7. Run semantic red confirmation.
8. Implement the smallest production change that can make the focused test pass.
9. Run the green gate with the same targeted command used for red.
10. Run full check before claiming completion.
11. Run review and inspect the final diff.

Do not claim TDD Harness Mode completion when `./scripts/tdd-cycle check --task
<task-id>` failed or was not run.

## Clarification Gate

Ask the developer before generating tests when a decision affects user-visible
behavior, API contracts, security, permissions, data model, billing, side
effects, performance budgets, or backwards compatibility.

Do not add Playwright or browser-test dependencies without developer approval.
If Playwright already exists and the developer wants browser verification, prefer
the repository's existing Playwright command and test conventions.
