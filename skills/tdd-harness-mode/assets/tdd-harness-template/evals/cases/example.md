# Evaluation Case Example

Use this format for reusable regression cases.

## ID

auth-rate-limit

## Prompt

Add rate limiting to failed login attempts. After five failed attempts from the
same IP address, the sixth attempt must return HTTP 429. A successful login
resets the failure counter.

## Acceptance Criteria

- [ ] Six failed attempts from one IP produce a 429 response.
- [ ] Failed attempts from different IPs are counted independently.
- [ ] Successful login resets the counter.
- [ ] Existing login behavior remains compatible.

## Required Test Shape

- A focused regression test fails before implementation.
- The test verifies observable HTTP behavior or service contract behavior.
- The full suite passes after implementation.

## Suggested Targeted Command

```bash
./scripts/tdd-cycle plan \
  --summary "Failed login rate limiting is covered by a focused auth regression test." \
  --test-command "pytest tests/test_auth.py::test_failed_login_rate_limit" \
  --playwright not-applicable
./scripts/tdd-cycle red -- ./scripts/test-target pytest tests/test_auth.py::test_failed_login_rate_limit
./scripts/tdd-cycle confirm-red \
  --category missing-behavior \
  --reason "The focused regression test fails because failed login attempts are not rate limited yet."
./scripts/tdd-cycle green -- ./scripts/test-target pytest tests/test_auth.py::test_failed_login_rate_limit
```

## Review Questions

- Did the agent prove red before modifying production code?
- Did the agent record a plan gate before red?
- Did the agent confirm semantic red before implementation?
- Did the implementation avoid global counters that leak across tenants?
- Did the agent add cleanup or fixture isolation for the rate limit state?
- Did the final check include the existing login test suite?
