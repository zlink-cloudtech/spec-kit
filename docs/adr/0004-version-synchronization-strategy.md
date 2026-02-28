# 4. Single-Version Synchronization Strategy

**Date**: 2026-02-26
**Status**: Accepted

## Context

The Speckit MCP server has multiple versioned artifacts that are released together:

1. **NPM package** (`speckit-mcp-server`): Versioned in `mcp/package.json`.
2. **Docker image** (`speckit-mcp-server`): Tagged with the NPM package version.
3. **Helm chart** (`speckit-mcp-server`): Has both a `version` (chart version) and `appVersion` (application version) in `Chart.yaml`.

Helm conventionally allows chart versions and app versions to diverge (e.g., chart v2.0.0 deploying app v1.5.3). This enables independent chart evolution. However, it also creates confusion about which chart version corresponds to which application version.

### Alternatives Considered

- **Independent chart versioning**: Rejected because it adds cognitive overhead — users must know both the chart version and the app version, and the mapping between them is not obvious.
- **Manual version updates in Chart.yaml**: Rejected because it's error-prone and not automated — developers may forget to update the chart version when bumping the application version.

## Decision

Use a single version from `mcp/package.json` for all three artifacts: NPM package, Docker image, and Helm chart. The `Chart.yaml` contains placeholder version values (`0.0.0`) that are overridden at packaging time by the release workflow:

```bash
MCP_VERSION=$(jq -r '.version' mcp/package.json)
helm package mcp/chart --version "$MCP_VERSION" --app-version "$MCP_VERSION"
```

This means:

- `Chart.yaml.version` = `mcp/package.json.version` (at package time)
- `Chart.yaml.appVersion` = `mcp/package.json.version` (at package time)
- Docker image tag = `mcp/package.json.version`
- NPM package version = `mcp/package.json.version`

The `mcp/scripts/publish-chart.sh` helper script reads from `mcp/package.json` and passes the version to `helm package` and `helm push`.

## Consequences

### Positive

- Single source of truth — one version bump propagates to all artifacts.
- Clear correlation — chart version X always deploys application version X.
- Simplified release workflow — no manual version coordination needed.
- Users can reason about versions easily: `helm install ... --version 1.2.3` installs app version 1.2.3.

### Negative

- Chart cannot be independently versioned — a chart-only fix (e.g., template tweak) requires bumping the full application version.
- Breaks the conventional Helm practice of decoupled chart/app versioning.
- `Chart.yaml` shows `0.0.0` in source control, which may confuse developers inspecting the repo (mitigated by comments in the file).
