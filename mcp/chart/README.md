# Speckit MCP Server Helm Chart

A Helm chart for deploying the [Speckit MCP Server](../README.md) to Kubernetes with dual-mode support: pre-built container image or runtime NPM package installation.

## Features

- **Dual deployment modes**: Deploy via container image (`image`) or NPM package (`npm`)
- **Flexible networking**: Support for both Kubernetes Ingress and Gateway API HTTPRoute (mutually exclusive)
- **Configurable resources**: CPU/memory requests and limits, replica count, node scheduling
- **Private registry support**: Image pull secrets and NPM authentication secrets
- **Helm best practices**: Standard labels (`app.kubernetes.io/*`), JSON schema validation, liveness/readiness probes
- **OCI distribution**: Published to GHCR as an OCI artifact

## Prerequisites

- Kubernetes 1.24+
- Helm 3.8+
- Access to GitHub Container Registry (GHCR) for chart and image pulls

## Installation

### From GHCR (OCI Registry)

```bash
# Install with default values (image mode)
helm install my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server --version <version>

# Install with NPM mode
helm install my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server \
  --version <version> \
  --set mode=npm
```

### From Local Source

```bash
# Clone the repo and install from local chart
helm install my-mcp ./mcp/chart

# With custom values file
helm install my-mcp ./mcp/chart -f my-values.yaml
```

## Deployment Modes

### Image Mode (Default)

Deploys the MCP server using a pre-built container image.

```bash
helm install my-mcp ./mcp/chart \
  --set mode=image \
  --set image.repository=ghcr.io/speckit/mcp-server \
  --set image.tag=0.1.1
```

### NPM Mode

Deploys the MCP server by installing the NPM package at runtime using an init container.

```bash
helm install my-mcp ./mcp/chart \
  --set mode=npm \
  --set npm.package=@speckit/mcp-server \
  --set npm.version=0.1.1
```

For private NPM registries, create a secret with your `.npmrc` and reference it:

```bash
# Create the authentication secret
kubectl create secret generic npm-auth \
  --from-literal=.npmrc="//registry.example.com/:_authToken=YOUR_TOKEN"

# Install with auth secret
helm install my-mcp ./mcp/chart \
  --set mode=npm \
  --set npm.registry=https://registry.example.com \
  --set npm.authSecret=npm-auth
```

## Configuration

### Values Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `mode` | Deployment mode: `image` or `npm` | `image` |
| **Image Mode** | | |
| `image.repository` | Container image repository | `ghcr.io/speckit/mcp-server` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy (`Always`, `IfNotPresent`, `Never`) | `IfNotPresent` |
| `image.pullSecrets` | List of image pull secret names | `[]` |
| **NPM Mode** | | |
| `npm.package` | NPM package name | `@speckit/mcp-server` |
| `npm.version` | NPM package version | `latest` |
| `npm.registry` | NPM registry URL | `https://registry.npmjs.org` |
| `npm.authSecret` | Name of Secret containing `.npmrc` for auth | `""` |
| **Service** | | |
| `service.type` | Kubernetes Service type (`ClusterIP`, `NodePort`, `LoadBalancer`) | `ClusterIP` |
| `service.port` | Service port | `8080` |
| `service.targetPort` | Container target port | `8080` |
| `service.annotations` | Service annotations | `{}` |
| **Resources** | | |
| `replicas` | Number of pod replicas | `1` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.requests.memory` | Memory request | `128Mi` |
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| **Scheduling** | | |
| `nodeSelector` | Node selector labels | `{}` |
| `tolerations` | Pod tolerations | `[]` |
| `affinity` | Pod affinity rules | `{}` |
| **Ingress** | | |
| `ingress.enabled` | Enable Ingress resource | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress host configurations | See `values.yaml` |
| `ingress.tls` | TLS configurations | `[]` |
| **HTTPRoute (Gateway API)** | | |
| `httpRoute.enabled` | Enable HTTPRoute resource | `false` |
| `httpRoute.gatewayName` | Gateway resource name | `""` |
| `httpRoute.gatewayNamespace` | Gateway namespace (defaults to release namespace) | `""` |
| `httpRoute.hostnames` | Hostnames for routing | `["mcp.example.com"]` |
| `httpRoute.annotations` | HTTPRoute annotations | `{}` |

> **Note**: `ingress` and `httpRoute` are mutually exclusive. Enabling both will cause a template rendering error.

### Example Values File

```yaml
mode: image

image:
  repository: ghcr.io/myorg/custom-mcp
  tag: "2.0.0"
  pullPolicy: Always

replicas: 3

resources:
  requests:
    cpu: 200m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: mcp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: mcp-tls
      hosts:
        - mcp.example.com
```

## Networking

### Ingress

Enable traditional Kubernetes Ingress for external access:

```bash
helm install my-mcp ./mcp/chart \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set 'ingress.hosts[0].host=mcp.example.com' \
  --set 'ingress.hosts[0].paths[0].path=/' \
  --set 'ingress.hosts[0].paths[0].pathType=Prefix'
```

### HTTPRoute (Gateway API)

Enable Gateway API HTTPRoute for modern Kubernetes networking:

```bash
helm install my-mcp ./mcp/chart \
  --set httpRoute.enabled=true \
  --set httpRoute.gatewayName=my-gateway \
  --set 'httpRoute.hostnames[0]=mcp.example.com'
```

For cross-namespace Gateway references:

```bash
helm install my-mcp ./mcp/chart \
  --set httpRoute.enabled=true \
  --set httpRoute.gatewayName=shared-gateway \
  --set httpRoute.gatewayNamespace=gateway-system \
  --set 'httpRoute.hostnames[0]=mcp.example.com'
```

## Validation

### Lint the Chart

```bash
helm lint mcp/chart
```

### Render Templates Locally

```bash
# Default values (image mode)
helm template test mcp/chart

# With test values
helm template test mcp/chart -f mcp/chart/ci/test-values-image.yaml
helm template test mcp/chart -f mcp/chart/ci/test-values-npm.yaml
```

### Dry-Run Install

```bash
helm install my-mcp mcp/chart --dry-run --debug
```

## Upgrading

```bash
# Upgrade to a new chart/image version
helm upgrade my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server --version <new-version>

# Update configuration while keeping current version
helm upgrade my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server \
  --reuse-values \
  --set replicas=3
```

## Uninstalling

```bash
helm uninstall my-mcp
```

## Troubleshooting

### Pod Not Starting (Image Mode)

```bash
kubectl describe pod <pod-name>
# Look for ImagePullBackOff — verify image.repository and image.tag
# Check image pull secrets for private registries
```

### Init Container Failing (NPM Mode)

```bash
kubectl logs <pod-name> -c npm-install
# E401: Check npm.authSecret configuration
# ENOTFOUND: Check npm.registry URL
# E404: Check npm.package name
```

### Mode Validation Error

```text
execution error: Invalid deployment mode 'X'. Must be 'image' or 'npm'
```

Set `mode` to a valid value: `--set mode=image` or `--set mode=npm`.

### Routing Conflict

```text
execution error: Cannot enable both ingress and httpRoute
```

Only one of `ingress.enabled` or `httpRoute.enabled` can be `true`.

## Development

### Test Values Files

The `ci/` directory contains test values files used for validation:

| File | Purpose |
|------|---------|
| `ci/test-values-image.yaml` | Image mode deployment |
| `ci/test-values-npm.yaml` | NPM mode deployment |
| `ci/test-values-npm-auth.yaml` | NPM mode with auth secret |
| `ci/test-values-ingress.yaml` | Ingress configuration |
| `ci/test-values-httproute.yaml` | HTTPRoute configuration |
| `ci/test-values-conflict.yaml` | Mutual exclusivity validation (expected failure) |

### Publishing

The chart is automatically packaged and published to GHCR as part of the [release workflow](../../.github/workflows/release-mcp-publish.yml). You can also publish manually:

```bash
./mcp/scripts/publish-chart.sh <version>
```

## License

This chart is part of [Spec Kit](https://github.com/zlink-cloudtech/spec-kit) and is licensed under the MIT License.
