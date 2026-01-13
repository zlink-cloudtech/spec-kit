# Feature Specification: Split Release Server Publish Workflow

**Feature Branch**: `005-split-publish-workflow`
**Created**: 2026-01-13
**Status**: Draft
**Input**: Split release-server-publish workflow into test and publish jobs

## Clarifications

### Session 2026-01-13
- Q: The spec includes separate test and publish jobs. How should data/state be passed between them? → A: Option A - Independent Execution: The publish job will check out the code again and set up its own environment (no artifact passing) to ensure a clean build context.
- Q: How should the version bump calculated in the 'publish' job be handled? → A: Option A - Push with [skip ci]: The workflow will commit version changes and push them back to the repository, including `[skip ci]` in the commit message to prevent recursive workflow triggers.
- Q: Since the publish job pushes changes to the repo, how should concurrent pipeline runs be handled? → A: Option A - Sequential Queueing: Use `concurrency: group: release-server-publish` to ensure workflows run one at a time, preventing git push conflicts.
- Q: What should happen if the 'publish' job determines the calculated version already exists as a tag/release? → A: Option A - Fail Workflow: The workflow should exit with an error to prevent overwrites or ambiguity, requiring manual resolution.
- Q: Should the split jobs reside in the same workflow file or be split into separate files? → A: Option B - Single Workflow File: Maintain `release-server-publish.yml` and define the `test` and `publish` jobs within it to preserve the pipeline visualization.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pull Request Validation (Priority: P1)

As a developer, when I submit a Pull Request to the release server, I want the CI to run tests automatically without attempting to publish artifacts, so that I can ensure my changes are valid without side effects.

**Why this priority**: Essential to prevent broken code from merging and to avoid accidental releases from PRs.

**Independent Test**: Can be fully tested by opening a PR with changes to `release-server/` and verifying that the `test` job runs while the `publish` job is skipped or does not exist for the PR context.

**Acceptance Scenarios**:

1. **Given** a new Pull Request targeting main, **When** the workflow triggers, **Then** the `test` job executes successfully.
2. **Given** a new Pull Request, **When** the workflow triggers, **Then** the `publish` job is NOT executed.
3. **Given** a Pull Request with failing tests, **When** the workflow triggers, **Then** the `test` job fails and the workflow is marked as failed.

### User Story 2 - Safe Release on Main (Priority: P1)

As a maintainer, when code is pushed to the `main` branch, I want the system to run tests first and only publish artifacts if the tests pass, so that I do not release broken software.

**Why this priority**: Ensures the integrity of the release process.

**Independent Test**: Can be tested by simulating a push to main (or using `workflow_dispatch` which mimics the main branch behavior for publishing).

**Acceptance Scenarios**:

1. **Given** a push to `main`, **When** the workflow triggers, **Then** the `test` job executes first.
2. **Given** the `test` job passes, **When** it completes, **Then** the `publish` job starts and executes.
3. **Given** the `test` job fails, **When** it completes, **Then** the `publish` job is skipped and no artifacts are released.

## Functional Requirements *(mandatory)*

### 1. Workflow Job Structure
- The `release-server-publish.yml` workflow MUST be maintained as a single file but divided into two distinct jobs: `test` and `publish`.
- **Concurrency**: The workflow MUST use `concurrency` with `group: release-server-publish` and `cancel-in-progress: false` (implied by sequential requirement) to prevent race conditions during version bumping.

### 2. Test Job
- **Triggers**: Must run on both `pull_request` events and `push` events to `main` (and `workflow_dispatch`).
- **Permissions**: Should require minimal permissions (e.g., `contents: read`).
- **Steps**:
  - Checkout code.
  - Setup Python 3.12.
  - Install `uv` package manager.
  - Install dependencies (`uv sync --all-extras`).
  - Run tests (`uv run pytest`).

### 3. Publish Job
- **Dependencies**: Must declare a dependency on the `test` job (`needs: test`).
- **Conditions**: Must ONLY run if `github.event_name != 'pull_request'`.
- **Permissions**: Requires write permissions for `contents` (to create releases/tags) and `packages` (to push to GHCR).
- **Execution Strategy**: Independent Execution (Fresh checkout and tool setup; does not consume artifacts from 'test').
- **Conflict Handling**: If calculated version tag already exists, the job MUST fail immediately.
- **Steps**:
  - Checkout code (fetch-depth 0).
  - Setup Python 3.12 & Install `uv`.
  - Calculate next version.
  - Check if release exists.
  - Generate release notes.
  - Update version files.
  - Login to GHCR.
  - Build and Push Docker image.
  - Package and Publish Helm Chart.
  - Create GitHub Release.
  - Commit version bump (if applicable) and Push to `main` with `[skip ci]` in the commit message.

## Success Criteria *(mandatory)*

- **Test Isolation**: PRs execute ONLY the test logic, saving resources and reducing noise.
- **Fail-Safe Publishing**: Releases are physically impossible (in the workflow logic) if tests have not passed in the same run.
- **Efficiency**: The `publish` job reuses the checkout or re-initializes efficiently, maintaining the reliability of the release process.
- **Visual Feedback**: GitHub Actions UI clearly reveals two separate phases (Test -> Publish), making it easier to diagnose dependencies vs. deployment failures.

## Assumptions & Dependencies *(optional)*

- **Assumptions**:
   - The current steps for testing and publishing in the existing file are correct and only need to be moved/restructured.
   - `uv` is the standard tool for dependency management in this project.
   - The runner environment (ubuntu-latest) supports all necessary commands.
