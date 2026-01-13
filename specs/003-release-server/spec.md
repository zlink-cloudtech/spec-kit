# Feature Specification: Release Server

**Feature Branch**: `003-release-server`
**Created**: 2026-01-06
**Status**: Draft
**Input**: User description: ""

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publish and Host Release Packages (Priority: P1)

As a release engineer, I want to publish `spec-kit` template packages to the Release Server so that they are available for distribution without relying on GitHub Releases.

**Why this priority**: Core functionality to support hosting and distribution of packages.

**Independent Test**: Can upload a file to the server and verify it is stored and listed. Try uploading a duplicate without flag (fails) and with flag (succeeds).

**Acceptance Scenarios**:

1. **Given** a running Release Server, **When** I upload a package (e.g., via HTTP POST), **Then** the package is stored successfully.
2. **Given** a file already exists, **When** I upload it again without the `overwrite` flag, **Then** the server returns 409 Conflict.
3. **Given** a file already exists, **When** I upload it with `overwrite=true`, **Then** the file is replaced and returns 200 OK.
4. **Given** stored packages, **When** I request the release metadata endpoint (simulating GitHub API), **Then** it returns a JSON response compatible with `specify init --template-url` expectations (containing asset URLs).
5. **Given** a stored package, **When** I request the download URL, **Then** the file is downloaded correctly.

---

### User Story 2 - Automated Package Cleanup (Priority: P2)

As a system administrator, I want the server to automatically delete old packages when a limit is reached to prevent disk space exhaustion.

**Why this priority**: Essential for maintenance-free operation of the release-server.

**Independent Test**: Configure limit to N, upload N+1, verify count is N and oldest is gone.

**Acceptance Scenarios**:

1. **Given** the server is configured with `max_packages: 5`, **When** I upload the 6th package, **Then** the oldest package is deleted and only 5 remain.

---

### User Story 3 - Deployment and Configuration (Priority: P2)

As a DevOps engineer, I want to deploy the server using Docker or Helm with configurable settings so that it fits my infrastructure standards.

**Why this priority**: Necessary for adoption and deployment in Kubernetes environments.

**Independent Test**: Build Docker image with custom tags, deploy via Helm with custom values.

**Acceptance Scenarios**:

1. **Given** the source code, **When** I build the Docker image with custom `REGISTRY` and `TAG` args, **Then** the resulting image has the correct name: `{REGISTRY}/{AUTHOR}/{IMAGE_NAME}:{TAG}`.
2. **Given** a Kubernetes cluster, **When** I install the provided Helm chart, **Then** the service starts and accepts connections on the configured port.
3. **Given** a YAML config file, **When** I start the server, **Then** it listens on the specified port.

---

### User Story 4 - Package Browsing (Priority: P3)

As a user, I want to see a list of available packages via a web interface or API so that I can verify what is published.

**Why this priority**: Specific requirement for visibility.

**Independent Test**: Visit `/packages` and see the list.

**Acceptance Scenarios**:

1. **Given** packages are stored, **When** I visit `/packages`, **Then** I see a list of available packages.

---

### User Story 5 - Package Deletion (Priority: P2)

As a release engineer, I want to delete a specific package using an API endpoint so that I can remove incorrect or deprecated releases.

**Why this priority**: Necessary for manual cleanup and correction.

**Independent Test**: Upload a file, verify it exists, send DELETE request, verify it is gone.

**Acceptance Scenarios**:

1. **Given** a stored package, **When** I send a DELETE request with valid auth token, **Then** the package is removed and the server returns 200 OK or 204 No Content.
2. **Given** a package, **When** I send a DELETE request without a token, **Then** the server returns 401 Unauthorized.
3. **Given** a non-existent package, **When** I send a DELETE request, **Then** the server returns 404 Not Found.

---

## Clarifications

### Session 2026-01-06
- Q: How should the server handle an upload if a file with the same name already exists? -> A: Reject by default (409 Conflict), but allow overwriting via an explicit `overwrite` query parameter.
- Q: Which Implementation Stack should be used? -> A: Python (to align with the CLI project).
- Q: How should the "max package count" limit be applied? -> A: Global limit (keep the most recent N files total, regardless of package name).
- Q: What is the default internal storage path for the container? -> A: `/data` (standard volume mount point).
- Q: What format should the package listing endpoint support? -> A: Both HTML (for humans) and JSON (for machine consumption).
- Q: How should the configuration file path be defined? -> A: Via an environment variable (e.g., `CONFIG_PATH`).
- Q: What authentication mechanism should be used for write operations? -> A: Bearer Token (Authorization header).
- Q: What logging format should be used? -> A: Structured JSON Logging (to stdout).

## Functional Requirements *(mandatory)*

### 1. HTTP Service
- **Protocol**: HTTP (HTTPS not required).
- **Stack**: Python (recommended: FastAPI or Flask).
- **Configuration**:
  - File format: YAML.
  - Path: Defined via `CONFIG_PATH` environment variable (default: `/etc/release-server/config.yaml`).
  - Configurable fields:
    - Listen port.
    - Max package count (retention policy).
    - Auth token (single shared secret for write operations).
- **Contract**: Implementation must validate against `contracts/openapi.yaml`.
- **API**:
  - GET `/latest`: Returns JSON matching GitHub Release structure (must include `assets` list).
  - GET `/assets/{filename}`: Downloads the file.
  - POST `/upload` (or similar): Accepts file upload for publishing.
    - **Authentication**: Requires `Authorization: Bearer <token>` header.
    - Query Parameter: `overwrite=true` (optional) to replace existing files.
  - DELETE `/assets/{filename}`: Deletes the package.
    - **Authentication**: Requires `Authorization: Bearer <token>` header.
  - GET `/packages`: Lists packages.
    - **Formats**: Support both HTML (list with links) and JSON (array of file metadata).
    - **Negotiation**: Support `Accept` header (`application/json`) OR query parameter `?format=json` (default: HTML).
  - GET `/healthz`: Liveness probe endpoint.
  - GET `/readyz`: Readiness probe endpoint.
- **Performance**:
  - Support file uploads up to ~100MB.
### 2. Package Management
- **Storage**: Store uploaded files on disk.
- **Cleanup**: Global limit strategy. On new upload, if total file count > `max_packages`, delete the file with the oldest modification time (across ALL files) before saving the new one.
- **Compatibility**: The metadata response must work with `specify --template-url`.

### 3. Containerization & Deployment
- **Docker**:
  - `Dockerfile` provided.
  - Build script/setup allowing custom `REGISTRY`, `AUTHOR` (Namespace), `IMAGE_NAME`, and `TAG`.
  - Image name format: `{REGISTRY}/{AUTHOR}/{IMAGE_NAME}:{TAG}`.
  - **Logging**: Application must output structured JSON logs to stdout for container observability.
    - **Schema**: Must include `level` (INFO, ERROR, etc.), `message`, `timestamp` (ISO 8601), and `module` (logger name).
- **Helm**:
  - Helm chart provided in `release-server/chart` (or similar).
  - Configurable values for image, port, persistence, and resources.
  - Support for both standard `Ingress` and `HTTPRoute` (Gateway API).
  - Configurable liveness and readiness probes (period, threshold).

### 4. Release Automation
- **CI/CD**:
  - Automated GitHub Action to build and publish Docker images.
  - Release script to package Helm charts and versioned artifacts.

## Success Criteria *(mandatory)*

- [ ] `specify init --template-url <server-url>/latest` successfully initializes a project using a package hosted on the server.
- [ ] Server limits stored packages to the configured number, automatically removing oldest.
- [ ] Docker image can be built with custom naming convention.
- [ ] Server can be deployed to Kubernetes using `helm install`.
- [ ] `/packages` returns a viewable list of packages.

## Assumptions *(optional)*

- Authentication is required for write operations (Bearer token), but read access is public.
- "GitHub Release Protocol" refers specifically to the JSON response format expected by `specify` CLI (providing direct download links).
- The server will handle single-file uploads per request.
- The Helm chart will use a standard Service/Deployment structure.
  - pod Namespace default to "spec-kit" if not provided.
- "Author" in image path maps to "Image Namespace" or "User" in Docker terms.
