# Quickstart: Testing Release Server Workflow

## Prerequisites
- A branch with changes to `release-server/`.
- `uv` installed locally for local verification.

## Local Testing
Verify tests pass locally before pushing:

```bash
cd release-server
uv sync --all-extras
uv run pytest
```

## Workflow Testing

### 1. Test PR Validation
1. Create a new branch `test/split-workflow`.
2. Make a dummy change to `release-server/README.md`.
3. Open a PR against `main`.
4. Verify that **only** the `test` job runs in the "Checks" section of the PR.
5. Verify `publish` job is skipped or not present.

### 2. Test Publication (Dry Run / Simulation)
Since actual publication requires permissions and pushing to `main`, use `workflow_dispatch` if enabled for testing, or rely on the `test` job passing in PRs.

To simulate `publish` logic locally (without publishing):
```bash
# Ensure you are logged in if needed, or dry-run scripts
# Scripts are in release-server/scripts/
```

## Troubleshooting

- **Test job fails**: Check `pytest` output in the actions log.
- **Publish job skipped on main**: Check `needs: test` status. If test failed, publish is skipped.
