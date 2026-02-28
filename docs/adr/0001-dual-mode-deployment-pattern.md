# 1. Dual-Mode Deployment Pattern (Image vs NPM)

**Date**: 2026-02-26
**Status**: Accepted

## Context

The Speckit MCP server needs to be deployable to Kubernetes via a Helm chart. Two distinct user personas exist:

1. **DevOps engineers** who prefer deploying pre-built container images — the standard Kubernetes deployment pattern.
2. **Platform engineers** who prefer installing the NPM package at runtime from an internal registry, avoiding container image distribution complexities.

Supporting both patterns within a single Helm chart avoids maintaining two separate charts and ensures a unified user experience. The key challenge is implementing conditional deployment logic that is maintainable, testable, and follows Kubernetes idioms.

### Alternatives Considered

- **Separate charts for each mode**: Rejected because it creates maintenance burden — two charts to test, version, and publish for what is essentially the same application.
- **Runtime mode detection via entrypoint logic**: Rejected because it pushes complexity into the container runtime and makes failures harder to diagnose.

## Decision

Use a single Helm chart with an explicit `mode` flag (`"image"` or `"npm"`) that drives conditional template logic:

- **Image mode** (`mode: "image"`, default): Standard Kubernetes Deployment with a user-specified container image, pull policy, and optional pull secrets.
- **NPM mode** (`mode: "npm"`): An init container runs `npm install --global` to install the MCP server package from a configurable registry into a shared `emptyDir` volume. The main container then runs the installed package from the shared volume.

Mode validation is fail-fast: if the `mode` value is neither `"image"` nor `"npm"`, `helm template` fails immediately with a descriptive error message using Helm's `fail` function in `_helpers.tpl`.

NPM authentication is handled by referencing an existing Kubernetes Secret containing `.npmrc` content, following the principle that credential management should be separated from chart deployment.

## Consequences

### Positive

- Single chart to maintain, test, and publish — reduces operational overhead.
- Init container pattern is idiomatic Kubernetes for runtime setup tasks.
- Fail-fast validation catches configuration errors before deployment.
- NPM auth via Secret reference follows Kubernetes security best practices.
- Default mode is `"image"`, providing the most straightforward experience for new users.

### Negative

- Conditional template logic in `deployment.yaml` is more complex than a single-mode chart.
- NPM mode init container adds startup latency (package download time).
- Users must understand the implications of each mode to choose appropriately.
- Testing requires separate CI values files for each mode (`ci/test-values-image.yaml`, `ci/test-values-npm.yaml`).
