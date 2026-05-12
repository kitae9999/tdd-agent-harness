# TDD Agent Harness

This repository is a reusable harness for agentic coding with a strict TDD loop.
It is meant to be copied into an application repo, then customized by editing
`scripts/check` and `scripts/test-target`.

The harness has one job: make it hard for an agent to skip the red/green/refactor
cycle or claim completion without executable evidence.

## What Is Included

- `AGENTS.md`: a short opt-in router for TDD Harness Mode.
- `TDD_HARNESS.md`: detailed TDD Harness Mode operating rules.
- `SPEC.md`: root task specification template.
- `TODO.md`: root task checklist template.
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

Append the TDD router section to an existing `AGENTS.md`:

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

`update` overwrites only managed core harness files:

- `TDD_HARNESS.md`
- `scripts/tdd-cycle`

It preserves project-owned files and prints review notes for them:

- `AGENTS.md`
- `harness.json`
- `SPEC.md`
- `TODO.md`
- `scripts/check`
- `scripts/test-target`

This keeps repo-specific test commands and agent instructions intact. Review the
printed project-owned files manually if you want to adopt new router guidance in
an existing `AGENTS.md`.

To append the small router section to an existing `AGENTS.md` during update:

```bash
tdd-agent-harness update /path/to/your-project --append-agents
```

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
the small TDD router section automatically:

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

TDD Harness Mode is opt-in. Use it when the developer explicitly asks for TDD
Harness Mode, TDD, or red/green/check/review. Ordinary coding requests should
follow the target repo's normal instructions. When TDD is requested, agents
should read `TDD_HARNESS.md` for the full workflow.

1. Start the TDD cycle:

```bash
./scripts/tdd-cycle start --id auth-rate-limit --reset
```

This creates task-local working files:

```text
.agent/tasks/auth-rate-limit/SPEC.md
.agent/tasks/auth-rate-limit/TODO.md
.agent/tasks/auth-rate-limit/state.json
.agent/tasks/auth-rate-limit/logs/
.agent/tasks/auth-rate-limit/report.md
```

Root `SPEC.md` and `TODO.md` are templates. For active TDD work, read and update
the task-local files shown by:

```bash
./scripts/tdd-cycle paths --task auth-rate-limit
```

2. Let the agent infer use cases and ask clarification questions for any product
   decision that changes correctness. For detailed UI or frontend-originated
   flows, the agent should ask whether to include Playwright/browser verification.
3. Record the plan gate:

```bash
./scripts/tdd-cycle plan --task auth-rate-limit \
  --summary "Rate limit failed login attempts by IP and reset on success." \
  --test-command "pytest tests/test_auth.py::test_rate_limit" \
  --playwright not-applicable
```

4. Write or ask the agent to write the failing test.
5. Prove the red phase:

```bash
./scripts/tdd-cycle red --task auth-rate-limit -- ./scripts/test-target pytest tests/test_auth.py::test_rate_limit
```

6. Confirm semantic red:

```bash
./scripts/tdd-cycle confirm-red --task auth-rate-limit \
  --category missing-behavior \
  --reason "The focused test fails because login failures are not rate limited yet."
```

7. Implement the smallest passing change.
8. Prove the green phase:

```bash
./scripts/tdd-cycle green --task auth-rate-limit -- ./scripts/test-target pytest tests/test_auth.py::test_rate_limit
```

9. Run the full verification gate:

```bash
./scripts/tdd-cycle check --task auth-rate-limit
```

10. Review the final diff and produce the report:

```bash
./scripts/tdd-cycle review --task auth-rate-limit
./scripts/tdd-cycle done --task auth-rate-limit
```

### Multi-Agent Work In One Worktree

Task-local mode is the default. When multiple agents share one worktree, give
each agent a different task id:

```bash
./scripts/tdd-cycle start --id checkout-flow --reset
./scripts/tdd-cycle paths --task checkout-flow
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

Each task writes active documents and evidence under `.agent/tasks/<task-id>/`:

- `.agent/tasks/<task-id>/SPEC.md`
- `.agent/tasks/<task-id>/TODO.md`
- `.agent/tasks/<task-id>/state.json`
- `.agent/tasks/<task-id>/logs/`
- `.agent/tasks/<task-id>/report.md`

Use one task id per agent. Code files are still shared, so use separate git
worktrees or explicit path ownership for high-risk parallel edits.

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
1. Read `AGENTS.md`, `TDD_HARNESS.md`, `SPEC.md`, and relevant code.
2. Infer use cases and edge cases.
3. Ask clarification questions before test generation when a developer decision changes correctness.
   Ask whether to use Playwright/browser verification for detailed UI or frontend-originated flows.
4. Run `./scripts/tdd-cycle start --id <task-id> --reset`, then `./scripts/tdd-cycle paths --task <task-id>`.
5. Read and update the task-local `SPEC.md` and `TODO.md` printed by `paths`.
6. Run `./scripts/tdd-cycle plan --task <task-id> --summary ... --test-command ... --playwright ...`.
7. Write a failing test before implementation.
8. Run `./scripts/tdd-cycle red --task <task-id> -- <targeted test command>`.
9. Run `./scripts/tdd-cycle confirm-red --task <task-id> --category missing-behavior --reason ...`.
10. Implement the smallest change.
11. Run `./scripts/tdd-cycle green --task <task-id> -- <targeted test command>`.
12. Run `./scripts/tdd-cycle check --task <task-id>`.
13. Run `./scripts/tdd-cycle review --task <task-id>`.
14. Summarize changed files, test results, and residual risk.
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

Task-local runs keep each task's documents, state, logs, and report under
`.agent/tasks/<task-id>/`. Same-task concurrent edits are still a coordination
problem, so split agents by task id or worktree.

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
