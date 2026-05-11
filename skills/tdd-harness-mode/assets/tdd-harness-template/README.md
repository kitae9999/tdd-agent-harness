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
- `scripts/tdd-cycle`: phase gate runner that records state and logs.
- `scripts/test-target`: targeted test wrapper.
- `scripts/check`: full verification wrapper.
- `docs/harness-design.md`: architecture and adaptation notes.
- `evals/cases/example.md`: example regression/evaluation case format.

## Quick Start

1. Copy these files into the target project.
2. Edit `scripts/check` so it runs the project's full verification suite.
3. Use `SPEC.md` to describe the next feature or bug fix.
4. Start the TDD cycle:

```bash
./scripts/tdd-cycle start --id auth-rate-limit --spec SPEC.md
```

5. Let the agent infer use cases and ask clarification questions for any product
   decision that changes correctness. For detailed UI or frontend-originated
   flows, the agent should ask whether to include Playwright/browser verification.
6. Record the plan gate:

```bash
./scripts/tdd-cycle plan \
  --summary "Rate limit failed login attempts by IP and reset on success." \
  --test-command "pytest tests/test_auth.py::test_rate_limit" \
  --playwright not-applicable
```

7. Write or ask the agent to write the failing test.
8. Prove the red phase:

```bash
./scripts/tdd-cycle red -- ./scripts/test-target pytest tests/test_auth.py::test_rate_limit
```

9. Confirm semantic red:

```bash
./scripts/tdd-cycle confirm-red \
  --category missing-behavior \
  --reason "The focused test fails because login failures are not rate limited yet."
```

10. Implement the smallest passing change.
11. Prove the green phase:

```bash
./scripts/tdd-cycle green -- ./scripts/test-target pytest tests/test_auth.py::test_rate_limit
```

12. Run the full verification gate:

```bash
./scripts/tdd-cycle check
```

13. Review the final diff and produce the report:

```bash
./scripts/tdd-cycle review
./scripts/tdd-cycle done
```

Generated logs and state are written under `.agent/`.

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
