# Harness Design

This harness separates agent behavior from project verification.

## Layers

1. Agent router: `AGENTS.md`
2. Detailed TDD instructions: `TDD_HARNESS.md`
3. Root task templates: `SPEC.md`, `TODO.md`
4. Task-local documents, state, and logs:
   - `.agent/tasks/<task-id>/SPEC.md`
   - `.agent/tasks/<task-id>/TODO.md`
   - `.agent/tasks/<task-id>/state.json`
   - `.agent/tasks/<task-id>/logs/`
   - `.agent/tasks/<task-id>/report.md`
5. Gate runner: `scripts/tdd-cycle`
6. Project commands: `scripts/test-target`, `scripts/check`

The gate runner does not know the target language or framework. It only enforces
phase order and records evidence.

## Lifecycle

```text
start
  -> doctor        optional environment readiness check
  -> plan          records inferred use cases, decisions, and targeted command
  -> ui-decision   records browser verification choice for UI/front-end flows
  -> red    expects targeted command to fail
  -> confirm-red confirms the failure is semantically meaningful
  -> green  expects targeted command to pass
  -> check  expects full verification to pass
  -> review writes final report
  -> done   requires full check
```

The red phase returns success when the targeted command fails, because the harness
goal is to prove that the new test catches missing behavior.

The green phase is blocked until semantic red is confirmed. A failed red caused
by syntax, imports, broken fixtures, timeouts, or environment setup does not prove
the missing behavior and should be fixed before implementation.

## State Layout

Task-local mode is the default. `start` always creates task-local documents and
evidence under `.agent/tasks/<task-id>/`:

```bash
./scripts/tdd-cycle start --id auth-rate-limit --reset
./scripts/tdd-cycle paths --task auth-rate-limit
./scripts/tdd-cycle plan --task auth-rate-limit --summary ... --test-command ... --playwright ...
./scripts/tdd-cycle red --task auth-rate-limit -- <targeted test command>
./scripts/tdd-cycle confirm-red --task auth-rate-limit --category missing-behavior --reason ...
./scripts/tdd-cycle green --task auth-rate-limit -- <same targeted test command>
./scripts/tdd-cycle check --task auth-rate-limit
./scripts/tdd-cycle review --task auth-rate-limit
```

Root `SPEC.md` and `TODO.md` are templates. In an active TDD task, agents should
read and update the task-local files printed by `paths`, not the root templates.

The task id is slugged for paths, so `Auth Rate Limit` writes under
`.agent/tasks/auth-rate-limit/`. Later commands select the task with
`--task <task-id>`, `TDD_HARNESS_TASK`, or `TDD_TASK_ID`. Use one task id per
agent; two agents intentionally writing to the same task id still need external
coordination.

## Adapting To A Project

### JavaScript or TypeScript

Edit `scripts/check` to run the project's real commands, for example:

```bash
pnpm lint
pnpm typecheck
pnpm test
```

Run a focused test with:

```bash
./scripts/tdd-cycle start --id auth-behavior --reset
./scripts/tdd-cycle plan --task auth-behavior \
  --summary "Auth behavior is covered by a focused component/unit test." \
  --test-command "pnpm vitest run src/auth/auth.test.ts" \
  --playwright not-applicable
./scripts/tdd-cycle red --task auth-behavior -- ./scripts/test-target pnpm vitest run src/auth/auth.test.ts
./scripts/tdd-cycle confirm-red --task auth-behavior --category missing-behavior --reason "The expected behavior is not implemented yet."
```

### Python

Use:

```bash
./scripts/tdd-cycle start --id auth-rate-limit --reset
./scripts/tdd-cycle plan --task auth-rate-limit \
  --summary "Rate limiting is covered by a focused auth regression test." \
  --test-command "pytest tests/test_auth.py::test_rate_limit" \
  --playwright not-applicable
./scripts/tdd-cycle red --task auth-rate-limit -- ./scripts/test-target pytest tests/test_auth.py::test_rate_limit
./scripts/tdd-cycle confirm-red --task auth-rate-limit --category missing-behavior --reason "The service does not enforce the limit yet."
```

Then set `scripts/check` to run:

```bash
pytest
ruff check .
mypy .
```

### Rust

Use:

```bash
./scripts/tdd-cycle start --id rate-limit --reset
./scripts/tdd-cycle plan --task rate-limit \
  --summary "Domain behavior is covered by a focused cargo test." \
  --test-command "cargo test rate_limit" \
  --playwright not-applicable
./scripts/tdd-cycle red --task rate-limit -- ./scripts/test-target cargo test rate_limit
./scripts/tdd-cycle confirm-red --task rate-limit --category missing-behavior --reason "The expected branch is not implemented yet."
```

Then set `scripts/check` to run:

```bash
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
```

## Policy Decisions

The harness intentionally avoids trying to infer correctness from model text.
Only command exit codes, logs, changed files, and explicit reports count as
evidence.

Recommended defaults:

- Plan gate must happen before red.
- Red must happen before green.
- Semantic red confirmation must happen before green.
- Green must happen before full check.
- Full check must happen before done.
- A test-looking file should change for feature/bug tasks.
- Review warns on likely test weakening, such as `.skip`, `.only`, assertion
  reduction, or snapshot churn.

## Doctor

Run:

```bash
./scripts/tdd-cycle doctor
```

The doctor checks harness files, executable bits, `.agent` gitignore coverage,
project markers, package scripts, CI workflow presence, and Playwright/browser
test detection. It records a state event when a task is active.

## Updating Existing Installs

Use the installed CLI to update an older harness inside an existing project:

```bash
tdd-agent-harness update /path/to/project --dry-run
tdd-agent-harness update /path/to/project
tdd-agent-harness update /path/to/project --append-agents
```

The update command is conservative. It refreshes managed core files such as
`TDD_HARNESS.md` and `scripts/tdd-cycle`, ensures `.agent/` is gitignored, and
runs doctor unless `--no-doctor` is passed.

It does not overwrite project-owned files:

- `AGENTS.md`
- `harness.json`
- `SPEC.md`
- `TODO.md`
- `scripts/check`
- `scripts/test-target`

Those files often contain repo-specific policy, task state, or verification
commands. The updater reports them so a developer can review template changes
manually.

With `--append-agents`, the updater appends only the small `AGENTS.md` router
that points to `TDD_HARNESS.md`. It does not append the full TDD policy into
`AGENTS.md`.

## UI And Browser Verification

For detailed UI changes or frontend-originated flows, ask the developer whether
browser-level verification should be included. Record the answer:

```bash
./scripts/tdd-cycle ui-decision \
  --playwright yes \
  --command "pnpm playwright test tests/checkout.spec.ts" \
  --reason "The requested change depends on browser routing and API state."
```

Do not add Playwright dependencies without explicit approval. If the repo already
has Playwright, prefer the existing scripts and conventions.

## Stronger Extensions

For stricter teams, add these gates:

- require a clean git worktree at `start`;
- fail review if no test file changed;
- run mutation tests for critical logic;
- run browser screenshots for UI changes;
- run a separate reviewer agent after green;
- require CI to execute `./scripts/tdd-cycle check`.

## Multi-Agent Flow

If using multiple agents in one worktree, give each independent task its own
task-local harness state and documents. If agents are collaborating on one
feature, prefer separate git worktrees or explicit ownership of files and phases.

Split responsibilities by phase:

```text
Planner: clarifies acceptance criteria and writes test plan
Test agent: writes the failing test
Coder: implements the smallest passing change
Reviewer: checks that tests were not weakened and the fix is scoped
Harness: records phase evidence and runs verification commands
```

Do not let planner, coder, and reviewer all share the same unchecked conclusion.
The harness should use executable checks as the source of truth.
