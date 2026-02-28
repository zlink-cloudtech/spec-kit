# 3. Gateway API HTTPRoute Support with Mutual Exclusivity

**Date**: 2026-02-26
**Status**: Accepted

## Context

The Helm chart needs to expose the MCP server to external traffic. Kubernetes offers two primary mechanisms for HTTP routing:

1. **Ingress** (`networking.k8s.io/v1`): The traditional approach, widely adopted and supported by many controllers (nginx, traefik, HAProxy, etc.).
2. **Gateway API HTTPRoute** (`gateway.networking.k8s.io/v1`): The next-generation routing API (GA since Kubernetes 1.26), offering more expressive routing, role-based ownership, and cross-namespace references.

Many organizations are in the process of migrating from Ingress to Gateway API. Supporting only one would exclude a significant user segment.

### Alternatives Considered

- **Ingress-only**: Rejected because it doesn't serve Gateway API adopters and positions the chart as backward-looking.
- **HTTPRoute-only**: Rejected because it's too aggressive — many production clusters still rely on Ingress controllers.
- **Both enabled simultaneously**: Rejected because simultaneous Ingress and HTTPRoute pointing to the same Service creates ambiguous routing behavior and potential traffic conflicts.

## Decision

Support both Ingress and Gateway API HTTPRoute as optional, mutually exclusive networking options:

- **`ingress.enabled: true`**: Renders a standard `networking.k8s.io/v1 Ingress` resource with configurable className, hosts, paths, and TLS.
- **`httpRoute.enabled: true`**: Renders a `gateway.networking.k8s.io/v1 HTTPRoute` resource with configurable gateway reference, hostnames, and backend configuration.
- **Mutual exclusivity**: If both `ingress.enabled` and `httpRoute.enabled` are `true`, template rendering fails immediately with a clear error message via Helm's `fail` function in `_helpers.tpl`.

The validation is implemented as:

```yaml
{{- if and .Values.ingress.enabled .Values.httpRoute.enabled }}
{{- fail "Cannot enable both ingress and httpRoute — they are mutually exclusive" }}
{{- end }}
```

When `httpRoute.enabled` is true, `httpRoute.gatewayName` is required (validated by the values schema).

## Consequences

### Positive

- Supports both legacy (Ingress) and modern (Gateway API) networking patterns.
- Users can migrate incrementally by switching from `ingress.enabled` to `httpRoute.enabled`.
- Fail-fast mutual exclusivity prevents ambiguous routing configurations.
- Gateway API HTTPRoute support future-proofs the chart for Kubernetes networking evolution.

### Negative

- Two networking templates to maintain and test (`ingress.yaml`, `httproute.yaml`).
- Users must understand the difference between Ingress and Gateway API to choose.
- Gateway API requires a Gateway controller and Gateway resource to be pre-configured in the cluster — the chart does not create these.
- Additional CI test values files needed for both paths (`ci/test-values-ingress.yaml`, `ci/test-values-httproute.yaml`, `ci/test-values-conflict.yaml`).
