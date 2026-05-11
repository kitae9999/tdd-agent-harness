# TDD Agent Harness

This repository is a reusable harness for agentic coding with a strict TDD loop.
It is meant to be copied into an application repo, then customized by editing
`scripts/check` and `scripts/test-target`.

The harness has one job: make it hard for an agent to skip the red/green/refactor
cycle or claim completion without executable evidence.

## What Is Included

- `AGENTS.md`: operating rules for coding agents.
- `SPEC.md`: task specification template focused on acceptance criteria.
- `TODO.md`: working checklist the agent keeps current.
- `harness.json`: policy and command configuration.
- `bin/tdd-agent-harness`: CLI entrypoint for installed copies.
- `scripts/tdd-cycle`: phase gate runner that records state and logs.
- `scripts/test-target`: targeted test wrapper.
- `scripts/check`: full verification wrapper.
- `scripts/install-harness`: conservative installer for existing repos.
- `scripts/update-harness`: safe updater for existing harness installs.
- `Formula/tdd-agent-harness.rb`: Homebrew-compatible formula for HEAD installs.
- `docs/harness-design.md`: architecture and adaptation notes.
- `evals/cases/example.md`: example regression/evaluation case format.

## Quick Start

### Option A: Homebrew-Compatible Install

This repository can be tapped directly with a custom Homebrew tap URL:

```bash
brew tap kitae9999/tdd-agent-harness https://github.com/kitae9999/tdd-agent-harness
brew install kitae9999/tdd-agent-harness/tdd-agent-harness
```

Then install the harness into a project:

```bash
tdd-agent-harness install /path/to/your-project
```

Append the TDD section to an existing `AGENTS.md`:

```bash
tdd-agent-harness install /path/to/your-project --append-agents
```

To install the latest `main` branch instead of the latest release:

```bash
brew install --HEAD kitae9999/tdd-agent-harness/tdd-agent-harness
```

### Updating An Existing Project

After upgrading the CLI, update an already-installed project safely:

```bash
brew update
brew upgrade tdd-agent-harness
tdd-agent-harness update /path/to/your-project --dry-run
tdd-agent-harness update /path/to/your-project
```

`update` overwrites only managed core harness files, currently
`scripts/tdd-cycle`. It preserves project-owned files and prints review notes for
them:

- `AGENTS.md`
- `harness.json`
- `SPEC.md`
- `TODO.md`
- `scripts/check`
- `scripts/test-target`

This keeps repo-specific test commands and agent instructions intact. Review the
printed project-owned files manually if you want to adopt new template guidance.

### Option B: Install From A Clone

Clone this repository somewhere outside your target project:

```bash
git clone https://github.com/kitae9999/tdd-agent-harness.git
```

Install the harness into your project:

```bash
cd tdd-agent-harness
./scripts/install-harness /path/to/your-project
```

You can also use the CLI from a clone:

```bash
./bin/tdd-agent-harness install /path/to/your-project
```

By default, the installer does not overwrite existing files. If your target repo
already has `AGENTS.md`, it prints a merge note instead of replacing it. To append
the TDD section automatically:

```bash
./scripts/install-harness /path/to/your-project --append-agents
```

Preview changes without writing files:

```bash
./scripts/install-harness /path/to/your-project --dry-run
```

After install, edit `scripts/check` in the target project so it runs that repo's
full verification suite.

### Option C: Use As A Codex Skill

If `tdd-harness-mode` is installed in Codex, you do not need to clone this repo
inside your target project. Open the target project and ask:

```text
TDD harness mode로 이 기능 구현해줘
```

The skill installs the bundled harness files if they are missing, preserving
existing `AGENTS.md`, `scripts/check`, and `scripts/test-target` unless you
explicitly ask it to merge or replace them.

### Run A TDD Cycle

1. Use `SPEC.md` to describe the next feature or bug fix.
2. Start the TDD cycle:

```bash
./scripts/tdd-cycle start --id auth-rate-limit --spec SPEC.md
```

3. Let the agent infer use cases and ask clarification questions for any product
   decision that changes correctness. For detailed UI or frontend-originated
   flows, the agent should ask whether to include Playwright/browser verification.
4. Record the plan gate:

```bash
./scripts/tdd-cycle plan \
  --summary "Rate limit failed login attempts by IP and reset on success." \
  --test-command "pytest tests/test_auth.py::test_rate_limit" \
  --playwright not-applicable
```

5. Write or ask the agent to write the failing test.
6. Prove the red phase:

```bash
./scripts/tdd-cycle red -- ./scripts/test-target pytest tests/test_auth.py::test_rate_limit
```

7. Confirm semantic red:

```bash
./scripts/tdd-cycle confirm-red \
  --category missing-behavior \
  --reason "The focused test fails because login failures are not rate limited yet."
```

8. Implement the smallest passing change.
9. Prove the green phase:

```bash
./scripts/tdd-cycle green -- ./scripts/test-target pytest tests/test_auth.py::test_rate_limit
```

10. Run the full verification gate:

```bash
./scripts/tdd-cycle check
```

11. Review the final diff and produce the report:

```bash
./scripts/tdd-cycle review
./scripts/tdd-cycle done
```

In the default single-task mode, generated state, logs, and reports are written
under `.agent/tdd-state.json`, `.agent/logs/`, and `.agent/report.md`.

### Parallel Agents In One Worktree

When multiple agents share one worktree, start each cycle in task-scoped mode:

```bash
./scripts/tdd-cycle start --id checkout-flow --parallel --reset
./scripts/tdd-cycle plan --task checkout-flow \
  --summary "Checkout behavior is covered by a focused regression test." \
  --test-command "pytest tests/test_checkout.py::test_checkout_flow" \
  --playwright not-applicable
./scripts/tdd-cycle red --task checkout-flow -- ./scripts/test-target pytest tests/test_checkout.py::test_checkout_flow
./scripts/tdd-cycle confirm-red --task checkout-flow \
  --category missing-behavior \
  --reason "The focused test fails because checkout completion is not implemented yet."
./scripts/tdd-cycle green --task checkout-flow -- ./scripts/test-target pytest tests/test_checkout.py::test_checkout_flow
./scripts/tdd-cycle check --task checkout-flow
./scripts/tdd-cycle review --task checkout-flow
./scripts/tdd-cycle done --task checkout-flow
```

Task-scoped mode writes evidence under `.agent/tasks/<task-id>/`:

- `.agent/tasks/<task-id>/state.json`
- `.agent/tasks/<task-id>/logs/`
- `.agent/tasks/<task-id>/report.md`

Use one task id per agent. Commands without `--parallel` and `--task` keep the
original single-task behavior.

## Agent Prompt Pattern

Use this prompt shape with Codex, Claude Code, OpenCode, or another coding agent:

```md
Work in TDD harness mode.

Goal:
- <feature or bug fix>

Success criteria:
- <observable behavior>
- <targeted test passes>
- `./scripts/tdd-cycle check` passes

Required sequence:
1. Read `AGENTS.md`, `SPEC.md`, and relevant code.
2. Infer use cases and edge cases.
3. Ask clarification questions before test generation when a developer decision changes correctness.
   Ask whether to use Playwright/browser verification for detailed UI or frontend-originated flows.
4. Run `./scripts/tdd-cycle plan --summary ... --test-command ... --playwright ...`.
   If multiple agents share one worktree, start with `./scripts/tdd-cycle start --id <task-id> --parallel --reset`
   and pass `--task <task-id>` to every later harness gate.
5. Update `TODO.md` with the test plan, assumptions, and resolved decisions.
6. Write a failing test before implementation.
7. Run `./scripts/tdd-cycle red -- <targeted test command>`.
8. Run `./scripts/tdd-cycle confirm-red --category missing-behavior --reason ...`.
9. Implement the smallest change.
10. Run `./scripts/tdd-cycle green -- <targeted test command>`.
11. Run `./scripts/tdd-cycle check`.
12. Run `./scripts/tdd-cycle review`.
13. Summarize changed files, test results, and residual risk.
```

## Policy

The default policy requires:

- a started task before red/green/check;
- a plan gate before red;
- a red event before green;
- a semantic red confirmation before green;
- a green event before full check;
- a full check before done;
- logs for every gate command;
- a final report before done.

For parallel agents in one worktree, task-scoped runs keep each task's state,
logs, and report under `.agent/tasks/<task-id>/`. Same-task concurrent edits are
still a coordination problem, so split agents by task id or worktree.

If the target project is a git repository, the review command also reports changed
files, warns when no test-looking file changed, flags likely test weakening, and
prints risk hints based on changed paths.

## Extra Commands

Use `doctor` before a first task or after installing the harness:

```bash
./scripts/tdd-cycle doctor
```

For detailed UI or frontend-originated flows, record the browser verification decision:

```bash
./scripts/tdd-cycle ui-decision \
  --playwright yes \
  --command "pnpm playwright test tests/checkout.spec.ts" \
  --reason "Checkout requires browser flow coverage from form submit to receipt."
```

## Customization

For most projects, only these two files need edits:

- `scripts/test-target`: how to run a focused test.
- `scripts/check`: how to run the full verification suite.

You can also update `harness.json` to change command names, test file patterns,
or policy strictness.

## License

MIT
