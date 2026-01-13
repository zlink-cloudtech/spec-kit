# Research: Split Release Server Publish Workflow

**Status**: Complete
**Date**: 2026-01-13

## Decisions

### 1. Job Separation Strategy
- **Decision**: Define two jobs, `test` and `publish`, in the same workflow file.
- **Rationale**: Keeps related logic together while ensuring strict ordering and separation of concerns. `test` runs on all relevant triggers, `publish` depends on `test` and only runs on release/main push events.
- **Alternatives Considered**: 
  - Separate workflow files: Harder to enforce "test must pass before publish" in the same context without using complex triggers or external events (workflow_run).
  - Single job with if conditions: Does not provide the visual separation and restartability of distinct jobs.

### 2. Dependency Management
- **Decision**: `needs: test` in the `publish` job.
- **Rationale**: GitHub Actions native dependency management ensures `publish` never starts if `test` fails or is skipped (unless `if: always()` is used, which we won't).

### 3. Artifact Handling
- **Decision**: No artifacts will be shared between jobs for now. `publish` will checkout clean.
- **Rationale**: The `test` job only verifies code correctness. `publish` builds from the verified commit. Since `version` calculation happens in `publish` (according to existing logic), we don't need to pass it from `test`.
- **Note**: If efficiency becomes an issue, we could build in `test` and upload artifacts, but for now cleanliness is preferred.

## Unknowns Resolved

- **Unknown**: How to handle version calculation?
- **Resolution**: Version calculation stays in the publish phase (or pre-publish) as it involves tagging/releasing. Testing doesn't need to know the next version, only that the code works.
