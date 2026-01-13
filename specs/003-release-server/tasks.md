# Tasks: Release Server

**Phase 1: Setup**
- [x] T001 Initialize project structure (release-server folder, pyproject.toml)
- [x] T002 Create Dockerfile and .dockerignore
- [x] T003 Implement Configuration loading (Pydantic settings) in release-server/src/release_server/config.py
- [x] T004 Setup Structured JSON logging in release-server/src/release_server/logging.py

**Phase 2: Foundation (Core Logic)**
- [x] T005 [P] Implement Storage Service (save, list, delete) in release-server/src/release_server/storage.py
- [x] T006 [P] Implement Auth Middleware (Bearer token for write ops) in release-server/src/release_server/auth.py
- [x] T007 Implement basic Package Service (list, upload logic) in release-server/src/release_server/services/package_service.py
- [x] T024 Implement main.py entrypoint and app wiring in release-server/src/release_server/main.py

**Phase 3: User Story 1 (Publish & Host - P1)**
- [x] T011 [US1] Define integration tests for upload flows (TDD) in release-server/tests/test_api.py
- [x] T008 [US1] Implement /upload endpoint (POST) in release-server/src/release_server/router.py
- [x] T022 [US1] Define integration tests for download flows (TDD) in release-server/tests/test_api.py
- [x] T009 [US1] Implement /latest endpoint (GitHub compatible) in release-server/src/release_server/router.py
- [x] T010 [US1] Implement /assets/{filename} endpoint (download) in release-server/src/release_server/router.py

**Phase 4: User Story 2 (Automated Cleanup - P2)**
- [x] T014 [US2] Add unit tests for retention policy (TDD) in release-server/tests/test_storage.py
- [x] T012 [US2] Implement cleanup logic (max packages check) in release-server/src/release_server/services/package_service.py
- [x] T013 [US2] Integrate cleanup as synchronous pre-save check in /upload endpoint

**Phase 5: User Story 3 (Deployment - P2)**
- [x] T015 [US3] Create Helm Chart structure in release-server/chart/
- [x] T016 [US3] Configure Helm values.yaml (image, auth, persistence)
- [x] T017 [US3] Verify Docker build arguments support (REGISTRY, IMAGE_NAME, TAG) and create scripts/build.sh
- [x] T027 [US3] Add HTTPRoute support to Helm Chart (mutually exclusive with Ingress)

**Phase 6: User Story 5 (Package Deletion - P2)**
- [x] T034 [US5] Define integration tests for delete endpoint (TDD) in release-server/tests/test_api.py
- [x] T035 [US5] Implement DELETE /assets/{filename} endpoint in release-server/src/release_server/router.py

**Phase 7: User Story 4 (Package Browsing - P3)**
- [x] T018 [US4] Implement /packages endpoint (HTML view) in release-server/src/release_server/router.py
- [x] T019 [US4] Implement content negotiation (JSON/HTML) for /packages using ?format=json and Accept header

**Phase 8: Polish**
- [x] T028 [Ops] Implement /healthz and /readyz endpoints in release-server/src/release_server/router.py
- [x] T029 [Ops] Make Helm probes configurable (period, threshold) in values.yaml
- [x] T020 Review and update README.md with deployment instructions
- [x] T021 Final full system test (manual verification of all flows)
- [x] T023 Validation of API implementation against contracts/openapi.yaml

**Phase 9: Release Automation (New Requirement)**
- [x] T025 Create release script to package Helm chart and artifacts in release-server/scripts/release.sh
- [x] T026 Create GitHub Action workflow for auto-publishing releases in .github/workflows/release-server-publish.yaml
- [x] T032 Create script to upload release packages in release-server/scripts/upload.sh
- [x] T033 Create script to publish Helm chart to GHCR in .github/workflows/scripts/publish-release-server-chart-ghcr.sh
- [x] T036 Create script to delete specific package in release-server/scripts/delete.sh

**Phase 10: Maintenance & Verification**
- [x] T030 Stabilize contract tests by ensuring environment isolation in tests/test_contract.py
- [x] T031 Document local workflow testing strategies (act) in release-server/README.md

## Dependencies

- Phase 2 depends on Phase 1
- Phase 3 depends on Phase 2
- Phase 4 depends on Phase 3
- Phase 5 depends on Phase 1 (Docker) and Phase 2 (Config)
- Phase 6 depends on Phase 2 (Foundation)
- Phase 7 depends on Phase 3 (List logic)
- Phase 9 depends on Phase 5 (Helm/Docker)

## Parallel Execution Opportunities

- T005 (Storage) and T006 (Auth) can be implemented in parallel.
- T015 (Helm) can start anytime after T002 (Docker).
- T018 (Browsing) can be implemented alongside T012 (Cleanup).
- T034/T035 (Deletion) can be implemented alongside T018 or T012.

## Implementation Strategy

We will build the core API server first (Setup + Foundation + US1) to enable the primary use case: hosting packages. Cleanup (US2), Deletion (US5), and Browsing (US4) are additive features. Deployment (US3) is parallel but verified at the end.
