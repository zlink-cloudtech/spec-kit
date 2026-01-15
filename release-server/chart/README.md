# Release Server Helm Chart

A Helm chart for deploying the `spec-kit` Release Server, a simple service for hosting spec-kit packages.

## Introduction

This chart bootstraps a [Release Server](https://github.com/zlink-cloudtech/spec-kit/tree/main/release-server) deployment on a [Kubernetes](http://kubernetes.io) cluster using the [Helm](https://helm.sh) package manager.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure (if persistence is enabled)

## Installation

### Method 1: Directly from OCI Registry (Recommended)

You can install the chart directly from GitHub Container Registry (GHCR):

```bash
helm install speckit-rs oci://ghcr.io/zlink-cloudtech/charts/speckit-rs --version 0.1.0
```

### Method 2: From Source (Local)

To install the chart from the local directory with the release name `speckit-rs`:

```bash
helm install speckit-rs ./chart
```

The command deploys the Release Server on the Kubernetes cluster in the default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

## Uninstalling

To uninstall/delete the `my-release` deployment:

```bash
helm uninstall my-release
```

The command removes all the Kubernetes components associated with the chart and deletes the release.

## Parameters

The following table lists the configurable parameters of the Release Server chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Image repository | `ghcr.io/zlink-cloudtech/speckit-rs` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `imagePullSecrets` | Image pull secrets | `[]` |
| `nameOverride` | Override name | `""` |
| `fullnameOverride` | Override full name | `""` |
| `serviceAccount.create` | Specifies whether a service account should be created | `true` |
| `serviceAccount.annotations` | Annotations to add to the service account | `{}` |
| `serviceAccount.name` | The name of the service account to use | `""` |
| `podAnnotations` | Pod annotations | `{}` |
| `podSecurityContext` | Pod security context | `{}` |
| `securityContext` | Container security context | `{}` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.hosts` | Ingress hosts | `[...]` |
| `resources` | CPU/Memory resource requests/limits | See `values.yaml` |
| `persistence.enabled` | Enable persistence | `true` |
| `persistence.storageClass` | Storage class | `""` |
| `persistence.accessMode` | Access mode | `ReadWriteOnce` |
| `persistence.size` | PVC size | `1Gi` |
| `persistence.path` | Mount path for data | `/data` |
| `app.port` | Application listening port | `8000` |
| `app.maxPackages` | Maximum number of packages to retain | `5` |
| `app.authToken` | Authentication token for write operations | `changeme` |
| `app.env` | Additional environment variables | See `values.yaml` |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example:

```bash
helm install my-release ./chart --set app.authToken=mysecuretoken
```

Alternatively, a YAML file that specifies the values for the above parameters can be provided while installing the chart. For example:

```bash
helm install my-release ./chart -f my-values.yaml
```

## Configuration

### Authentication

The Release Server requires an authentication token for write operations (uploading packages). The default value is `changeme`. It is **highly recommended** to change this value for production deployments.

You can set it via `--set app.authToken=YOUR_SECRET_TOKEN` or by providing a custom `values.yaml`.

### Persistence

The chart mounts a Persistent Volume at `/data` by default. This is where uploaded packages are stored. If you disable persistence (`persistence.enabled=false`), data will be lost when the pod restarts.
