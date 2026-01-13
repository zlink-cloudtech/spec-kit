# Research: Release Server

## Web Framework Selection

**Decision**: **FastAPI**

**Rationale**:
1.  **OpenAPI Support**: FastAPI automatically generates OpenAPI schema (`/openapi.json`), which satisfies the "Contract" requirement without extra dependencies.
2.  **Concurrency**: Async support handles multiple uploads efficiently.
3.  **Background Tasks**: Built-in `BackgroundTasks` support allows triggering cleanup logic *after* the response is sent, improving upload latency.
4.  **Simplicity**: Low boilerplate for a simple service compared to Flask + extensions.

**Alternatives Considered**:
*   **Flask**: Standard, but requires `flask-restx` or similar for OpenAPI. Synchronous by default.
*   **Django**: Overkill for a "lightweight" service.

## API Compatibility Strategy

**Decision**: **Replicate GitHub Releases API v3 (`GET /releases/latest`)**

**Rationale**:
The `specify` CLI (`src/specify_cli/__init__.py`) expects a JSON response with an `assets` list. Each asset must have:
*   `name`: Filename (must match `spec-kit-template-{ai}-{script}.zip` pattern).
*   `browser_download_url`: Direct link to download.
*   `size`: File size (optional but good for UX).

**Implementation**:
The GET endpoint (e.g., `/latest`) will list files in `/data` and construct this JSON structure dynamically.

## Automated Cleanup Strategy

**Decision**: **Background Task Triggered on Upload**

**Rationale**:
Running cleanup on every upload ensures the limit is enforcing "hard" constraints on disk usage. Using `BackgroundTasks` moves the IO operation out of the request/response cycle to keep the API snappy.

**Algorithm**:
1.  Receive file -> Save to `/data`.
2.  Return 200 OK.
3.  Background Task:
    *   List all files in `/data`.
    *   Sort by `mtime` (modified time).
    *   If count > `MAX_PACKAGES`:
        *   Delete oldest files until count == `MAX_PACKAGES`.

## Deployment Strategy

**Decision**: **Docker + Helm**

**Rationale**:
*   **Docker**: Multi-stage build (python:3.12-slim) to keep image size small. Run as non-root user for security.
*   **Helm**: Expose configuration (Max Packages, Persistence) via `values.yaml`.

**Configuration mapping**:
*   `MAX_PACKAGES` -> Environment Variable.
*   `STORAGE_PATH` -> Environment Variable (default `/data`).
*   `PORT` -> Environment Variable (default 8000).

## Observability & Security

**Decision**: **structlog + Bearer Auth**

**Rationale**:
*   **structlog**: Provides the required structured JSON output format for container logs (`{"level": "info", "event": "upload", ...}`).
*   **Bearer Auth**: Simple token checking middleware. Token source: `AUTH_TOKEN` env var.
*   **Config Loading**: Load from `CONFIG_PATH` yaml or Env vars using Pydantic Settings.
