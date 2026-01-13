# Implementation Plan: Split Release Server Publish Workflow

**Branch**: `005-split-publish-workflow` | **Date**: 2026-01-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The `release-server-publish.yml` workflow will be refactored into two distinct jobs: `test` and `publish`. The `test` job will run on all PRs and pushes to main to validate changes using `uv run pytest`. The `publish` job will depend on the `test` job and will only execute on non-PR events (e.g., push to main), performing the actual artifact building and publishing to GHCR and Helm repositories. This ensures no artifacts are published if tests fail and prevents accidental publishing from PRs.

## Technical Context

**Language/Version**: YAML (GitHub Actions), Python 3.12+ (Runtime)
**Primary Dependencies**: `uv` (Package Manager), GitHub Actions (Runner)
**Storage**: N/A
**Testing**: CI/CD testing via Workflow Triggers (PR vs Main)
**Target Platform**: GitHub Actions (ubuntu-latest)
**Project Type**: CI/CD Configuration
**Performance Goals**: Efficient job execution (cache reuse where possible)
**Constraints**: Must use existing `ubuntu-latest` runners
**Scale/Scope**: Refactor of single workflow file `release-server-publish.yml`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Alignment
*   **Library-First**: N/A - Workflow logic.
*   **Interface Compatibility**: N/A - Internal CI process.
*   **Test-First**: Compliant. The feature itself enables strict Test-First enforcement for releases.
*   **Integration Testing**: Verify workflow triggers (PR vs Push) work as expected.
*   **Observability**: Improved by splitting jobs (visual distinction in GitHub UI).

### Gate Status
*   **Status**: PASS

## Project Structure

### Documentation (this feature)

```text
specs/005-split-publish-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (N/A)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
.github/workflows/
└── release-server-publish.yml
```

**Structure Decision**: Modifying existing workflow file in `.github/workflows/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A
