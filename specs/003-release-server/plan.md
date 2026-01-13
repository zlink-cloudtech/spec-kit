# Implementation Plan: Release Server

**Feature Branch**: `003-release-server`
**Spec**: [spec.md](./spec.md)

## Summary

Implement a lightweight Python HTTP server to host and distribute `spec-kit` template packages. The server will support file uploads (publishing), automatic cleanup of old packages (retention policy), and serving metadata compatible with the GitHub Release format used by the `specify` CLI. Deployment will be managed via Docker and Helm.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: 
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `jinja2`: HTML templating
- `python-multipart`: File upload support
- `pydantic-settings`: Configuration management
**Storage**: Local filesystem (defaulting to `/data` volume)
**Testing**: `pytest` for unit/integration tests
**Target Platform**: Kubernetes (Linux container)
**Project Type**: Backend Service
**Constraints**: 
- Must handle ~100MB file uploads
- Must run as a non-root user in container

## Constitution Check

*GATE: Passed*
- **Library-First**: Core logic (storage, package service) separated from API router.
- **Interface Compatibility**: Validated against `contracts/openapi.yaml`.
- **Test-First**: TDD approach mandated for all user stories.
- **Observability**: Structured JSON logging required.

## Project Structure

### Documentation

```text
specs/003-release-server/
├── plan.md              # This file
├── research.md          # Research notes
├── data-model.md        # Data definitions
├── quickstart.md        # Usage guide
├── contracts/           # API contracts (OpenAPI)
├── checklists/          # Implementation checklists
└── tasks.md             # Execution tasks
```

### Source Code

```text
release-server/
├── chart/               # Helm chart
├── scripts/             # Build/Release scripts
├── src/
│   └── release_server/  # Application package
│       ├── main.py      # Entrypoint
│       ├── config.py    # Settings
│       ├── router.py    # API Routes
│       ├── services/    # Business Logic
│       └── templates/   # HTML templates
└── tests/               # Test suite
```

## Implementation Phases

**Phase 1: Setup**
Initialize project structure, environment configuration, and logging infrastructure.

**Phase 2: Foundation (Core Logic)**
Implement the core services: Storage abstractions (filesystem operations), Auth middleware (Bearer token), and basic Package service logic.

**Phase 3: User Story 1 (Publish & Host)**
Implement the primary API endpoints: Upload (`POST /upload`), Latest Metadata (`GET /latest`), and Download (`GET /assets/{filename}`).

**Phase 4: User Story 2 (Automated Cleanup)**
Implement the retention policy logic to automatically delete old packages when limits are reached.

**Phase 5: User Story 3 (Deployment)**
Create Docker container and Helm chart infrastructure for Kubernetes deployment.

**Phase 6: User Story 5 (Package Deletion)**
Add explicit delete capability (`DELETE /assets/{filename}`) for manual cleanup.

**Phase 7: User Story 4 (Package Browsing)**
Add a user-friendly HTML view (`GET /packages`) to list available artifacts.
Implement content negotiation via `Accept` header and `?format=json` query parameter (defaulting to HTML).

**Phase 8: Polish**
Operational readiness: Liveness/readiness probes, documentation updates, and valid contract testing.

**Phase 9: Release Automation**
Scripts and CI/CD workflows to publish the server image and Helm chart.

**Phase 10: Maintenance & Verification**
Stabilize tests and document local workflows.
