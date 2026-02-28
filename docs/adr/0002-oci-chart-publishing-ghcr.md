# 2. OCI Chart Publishing to GHCR

**Date**: 2026-02-26
**Status**: Accepted

## Context

The Speckit MCP Helm chart needs to be distributed to users for installation on their Kubernetes clusters. Helm supports multiple distribution mechanisms:

1. **Traditional Helm chart repository** (HTTP-based `index.yaml`): Requires hosting a web server or using GitHub Pages to serve an index file and chart tarballs.
2. **OCI registry** (Helm 3.8+): Stores charts as OCI artifacts alongside container images in any OCI-compliant registry.

The project already uses GitHub Container Registry (GHCR) for Docker images. Using the same registry for Helm charts simplifies infrastructure and authentication.

### Alternatives Considered

- **GitHub Pages-based Helm repo**: Rejected because it requires maintaining a separate `index.yaml`, a dedicated branch (e.g., `gh-pages`), and additional CI/CD steps to update the index on each release.
- **Third-party chart repository (e.g., ChartMuseum)**: Rejected because it introduces an external dependency and operational overhead.

## Decision

Publish the Helm chart as an OCI artifact to GitHub Container Registry (GHCR) using `helm push`. The release workflow (`.github/workflows/release-mcp-publish.yml`) handles:

1. **Version extraction** from `mcp/package.json` (single source of truth).
2. **Chart linting** with `helm lint` to catch errors before packaging.
3. **GHCR authentication** using `GITHUB_TOKEN` for zero-configuration CI/CD auth.
4. **Packaging** with `helm package mcp/chart --version <version>`.
5. **Publishing** with `helm push <chart>.tgz oci://ghcr.io/zlink-cloudtech/speckit-mcp-server`.
6. **Verification** with `helm install --dry-run --debug` against the published artifact.

A helper script `mcp/scripts/publish-chart.sh` encapsulates the packaging and push logic, following the same pattern as the existing `mcp/scripts/build-docker.sh`.

Users install the chart with:

```bash
helm install my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server --version <version>
```

## Consequences

### Positive

- No separate chart repository infrastructure needed — GHCR handles storage and versioning.
- Single authentication mechanism for both Docker images and Helm charts.
- OCI format is the modern Helm distribution standard (Helm 3.8+ default).
- `helm install oci://...` is a clean, direct installation UX.
- Automated verification in CI ensures every published chart is installable.

### Negative

- Requires Helm 3.8+ on client machines (older versions don't support OCI natively).
- GHCR OCI support for Helm charts is relatively newer; some organizations may not have adopted it yet.
- Users cannot browse chart versions via a web UI as easily as with traditional Helm repos (must use `helm search` or GHCR package UI).
