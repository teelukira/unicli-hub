# Skill: run-tests

Run the project's tests with the right command and interpret the results.

## When to Use

- Checking for regressions after a change.
- Confirming the current test state of a branch under review.

## Steps

1. Detect the project's build tool at the repo root (npm / pnpm / yarn, pytest, gradle, maven, cargo, `go test`, etc.).
2. Run either the full test suite or the subset relevant to the change.
3. If anything fails, summarize the likely cause from the stack trace or output.
4. Call out any slow or flaky tests you notice.

## Output

- The exact command you ran.
- Pass / fail summary.
- For each failure: file, test name, and suspected cause.
- Recommended follow-ups.

## Guard

- Do not "fix" a flaky test by re-running it — investigate the cause first.
- Do not delete or skip tests without explicit approval.
