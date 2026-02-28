# Helm Deployment: MCP Server on Kubernetes

## Overview

The Speckit MCP Server can be deployed to any Kubernetes 1.24+ cluster using the included Helm chart. The chart supports a **dual-mode deployment pattern** that lets you choose between two runtime strategies depending on your organization's infrastructure preferences.

## How It Works

### Architecture

```text
┌─────────────────────────────────────────────────────────┐
│  Kubernetes Cluster                                     │
│                                                         │
│  ┌─────────────┐      ┌──────────────────────────────┐  │
│  │   Service    │─────▶│   Deployment (MCP Server)    │  │
│  │  ClusterIP   │      │                              │  │
│  │  :8080       │      │  ┌────────────────────────┐  │  │
│  └──────┬───────┘      │  │  Mode: image           │  │  │
│         │              │  │  → runs container image │  │  │
│         │              │  │                         │  │  │
│         │              │  │  Mode: npm              │  │  │
│         │              │  │  → init: npm install    │  │  │
│         │              │  │  → runs from volume     │  │  │
│         │              │  └────────────────────────┘  │  │
│  ┌──────┴───────┐      └──────────────────────────────┘  │
│  │   Ingress    │                                        │
│  │     OR       │   ┌──────────────┐                     │
│  │  HTTPRoute   │   │  ConfigMap   │  (optional)         │
│  └──────────────┘   └──────────────┘                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Dual-Mode Deployment

The chart's `mode` flag determines how the MCP server binary is provided to the running pod:

#### Image Mode (default: `mode: "image"`)

The standard Kubernetes deployment pattern. A pre-built container image containing the MCP server is pulled and run directly.

**How it works**:

1. Kubernetes pulls the specified container image (`image.repository:image.tag`).
2. The container starts the MCP server process.
3. Readiness and liveness probes verify the server is healthy.

**Best for**: Organizations with container registries, CI/CD pipelines that build images, and standard Kubernetes workflows.

#### NPM Mode (`mode: "npm"`)

An alternative pattern where the MCP server NPM package is installed at runtime via an init container.

**How it works**:

1. An **init container** (Node.js Alpine) runs `npm install --global` to download the MCP server package from a configurable NPM registry.
2. The installed package is written to a shared `emptyDir` volume mounted at `/usr/local/lib/node_modules`.
3. The **main container** (also Node.js Alpine) starts and runs the MCP server from the shared volume.
4. If `npm.authSecret` is provided, the init container mounts a Kubernetes Secret as `.npmrc` for private registry authentication.

**Best for**: Organizations using internal NPM registries, teams that prefer package-manager-based distribution, or environments where container image distribution is restricted.

### Networking

The chart supports two mutually exclusive networking options:

- **Ingress** (`ingress.enabled: true`): Traditional `networking.k8s.io/v1` Ingress resource. Works with any Ingress controller (nginx, traefik, etc.).
- **Gateway API HTTPRoute** (`httpRoute.enabled: true`): Modern `gateway.networking.k8s.io/v1` HTTPRoute resource. Requires a Gateway controller and pre-configured Gateway resource.

Enabling both simultaneously is a configuration error — the chart will fail template rendering with a descriptive error message. See [ADR-0003](adr/0003-gateway-api-httproute-support.md) for the rationale.

### Version Synchronization

The chart version, Docker image tag, and NPM package version are all synchronized from `mcp/package.json`. When you install chart version `X.Y.Z`, it deploys application version `X.Y.Z`. See [ADR-0004](adr/0004-version-synchronization-strategy.md) for details.

## Chart Structure

```text
mcp/chart/
├── Chart.yaml            # Chart metadata (version overridden at package time)
├── values.yaml           # Default configuration
├── values.schema.json    # JSON schema for values validation
├── README.md             # Detailed chart documentation with values reference
├── ci/                   # Test values files for CI validation
│   ├── test-values-image.yaml
│   ├── test-values-npm.yaml
│   ├── test-values-npm-auth.yaml
│   ├── test-values-ingress.yaml
│   ├── test-values-httproute.yaml
│   └── test-values-conflict.yaml
└── templates/
    ├── _helpers.tpl       # Template helpers (labels, fullname, validation)
    ├── deployment.yaml    # Dual-mode deployment logic
    ├── service.yaml       # ClusterIP/NodePort/LoadBalancer service
    ├── configmap.yaml     # Optional MCP server configuration
    ├── ingress.yaml       # Conditional Ingress resource
    ├── httproute.yaml     # Conditional HTTPRoute resource
    └── NOTES.txt          # Post-install instructions
```

## Quick Install

```bash
# Install from GHCR (OCI registry)
helm install my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server --version <version>

# Install from local source
helm install my-mcp ./mcp/chart

# Install with NPM mode
helm install my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server \
  --set mode=npm \
  --set npm.version=<version>
```

## Key Decisions

The following architectural decisions were made during the design of this Helm chart:

| Decision | ADR | Summary |
|----------|-----|---------|
| Dual-mode deployment | [ADR-0001](adr/0001-dual-mode-deployment-pattern.md) | Single chart with `mode` flag for image vs npm |
| OCI chart publishing | [ADR-0002](adr/0002-oci-chart-publishing-ghcr.md) | Publish to GHCR as OCI artifact (no traditional Helm repo) |
| Gateway API support | [ADR-0003](adr/0003-gateway-api-httproute-support.md) | HTTPRoute alongside Ingress with mutual exclusivity |
| Version sync | [ADR-0004](adr/0004-version-synchronization-strategy.md) | Single version from `mcp/package.json` for all artifacts |

## Further Reading

- [Chart README](../mcp/chart/README.md) — Full values reference and configuration examples
- [Quickstart for this feature](../specs/002-mcp-chart-deployment/quickstart.md) — Step-by-step deployment walkthrough
- [Release Workflow](../.github/workflows/release-mcp-publish.yml) — CI/CD pipeline for chart publishing
