# Tasks: Split Release Server Publish Workflow

**Feature**: Split Release Server Publish Workflow
**Status**: In Progress

## Phase 1: Setup
- [x] T001 Analyze `release-server-publish.yml` to map existing steps to new jobs

## Phase 2: Foundational
- [x] T002 Verify `uv` and Python environment requirements for both jobs

## Phase 3: User Story 1 - Pull Request Validation
**Goal**: CI runs tests automatically on PRs without side effects.
**Independent Test criteria**: Open PR, verify only `test` job runs and passes.

- [x] T003 [US1] Define `test` job in `.github/workflows/release-server-publish.yml`
- [x] T004 [US1] Move "Set up Python", "Install uv", "Install dependencies", and "Run tests" to `test` job
- [x] T005 [US1] Configure `test` job permissions (`contents: read`) and triggers
- [x] T006 [US1] Ensure `test` job does NOT have permission to write packages or contents

## Phase 4: User Story 2 - Safe Release on Main
**Goal**: Publish artifacts only after successful tests on main branch.
**Independent Test criteria**: Push to main (simulation), verify `test` runs then `publish` runs.

- [x] T007 [US2] Define `publish` job in `.github/workflows/release-server-publish.yml`
- [x] T008 [US2] Configure `publish` job dependency (`needs: test`) and conditional (`if: github.event_name != 'pull_request'`)
- [x] T009 [US2] Add "Checkout" logic to `publish` job (fetch-depth: 0)
- [x] T010 [US2] Move "Get Next Version Info", "Determine Target Version", "Check if release already exists" to `publish` job
- [x] T011 [US2] Move "Generate release notes" to `publish` job
- [x] T012 [US2] Duplicate "Set up Python", "Install uv", "Install dependencies" to `publish` job (required for build/scripts)
- [x] T013 [US2] Move "Update version in pyproject.toml" to `publish` job
- [x] T014 [US2] Move "Log in to GHCR", "Downcase repository owner", "Extract metadata for Docker", "Build and push Docker image" to `publish` job
- [x] T015 [US2] Move "Set up Helm", "Package artifacts", "Publish Helm Chart" to `publish` job
- [x] T016 [US2] Move "Create Release" to `publish` job
- [x] T017 [US2] Review and exclude any PR-only commit logic from `publish` job
- [x] T022 [US2] Add step to Commit version bump and Push to main with '[skip ci]' to `publish` job

## Phase 5: Polish & Cross-Cutting Concerns
- [x] T018 Verify workflow syntax using a linter if available
- [x] T019 Ensure all `if` conditions in steps are cleaned up (redundant checks for PR can be removed since job-level check exists)
- [x] T023 [Global] Configure workflow `concurrency` with group `release-server-publish` to prevent race conditions

## Dependencies
US1 -> US2 (US2 depends on the existence of a clean `test` job structure to build upon, though technically they can be defined in one edit session, logically US1 defines the first half of the pipeline)

## Implementation Strategy
- We will modify the single file `.github/workflows/release-server-publish.yml`.
- We can perform the split in a single pass of edits, but conceptually we are defining `test` first then `publish`.

## Phase 6: Verification Script
**Goal**: Create a script to locally verify the workflow using `gh act`.

- [x] T020 Enhance `.github/workflows/scripts/test-release-server.sh` to support testing `pull_request` (test job only) and `push` (test+publish jobs) events via `gh act`
- [x] T021 Verify workflow split using the updated script
- [x] T024 Update release-server/README.md to document new workflow testing options (pull_request vs push)
