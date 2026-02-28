# System Map

**Purpose**: This document serves as a **centralized index** of all authoritative documentation for the project. It enables AI agents to quickly locate relevant context without scanning the entire codebase.

**Last Updated**: [DATE]

---

## Essential Artifacts

### 🏛️ Architecture & Design

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| System Architecture | [NEEDS CREATION] | ⚠️ Missing | N/A | High-level system components, layers, and boundaries |
| Database Schema | [NEEDS CREATION] | ⚠️ Missing | N/A | Entity-relationship diagrams, tables, and constraints |
| API Design | [NEEDS CREATION] | ⚠️ Missing | N/A | REST/GraphQL endpoints, contracts, and authentication |
| Component Diagram | [NEEDS CREATION] | ⚠️ Missing | N/A | Service interactions, dependencies, and data flow |

### 📐 Configuration & Infrastructure

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| Deployment Config | [NEEDS CREATION] | ⚠️ Missing | N/A | Environment setup, CI/CD pipelines, and infrastructure |
| Security Policies | [NEEDS CREATION] | ⚠️ Missing | N/A | Authentication, authorization, secrets management |
| Monitoring & Logging | [NEEDS CREATION] | ⚠️ Missing | N/A | Observability stack, metrics, alerts, and dashboards |

### 🧪 Quality & Testing

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| Test Strategy | [NEEDS CREATION] | ⚠️ Missing | N/A | Unit, integration, e2e test approaches and coverage goals |
| Performance Benchmarks | [NEEDS CREATION] | ⚠️ Missing | N/A | Load testing results, SLOs, and optimization targets |

### 📚 Decisions & Standards

| Artifact | Location | Status | Last Updated | Description |
|----------|----------|--------|--------------|-------------|
| ADR Index | `docs/adr/` | ✅ Active | [DATE] | Architectural Decision Records directory |
| Code Style Guide | [NEEDS CREATION] | ⚠️ Missing | N/A | Language-specific conventions and linting rules |
| Development Guidelines | [NEEDS CREATION] | ⚠️ Missing | N/A | Git workflow, PR process, and review standards |

---

## Integration Points

### External Services

| Service | Type | Documentation | Owner | Purpose |
|---------|------|--------------|-------|---------|
| [Example: Auth0] | Identity Provider | `docs/integrations/auth0.md` | Security Team | User authentication |
| [Example: Stripe] | Payment Gateway | `docs/integrations/stripe.md` | Backend Team | Payment processing |

### Internal Dependencies

| Module | Location | Interface | Maintainer | Description |
|--------|----------|-----------|------------|-------------|
| [Example: UserService] | `src/services/user` | `IUserService` | Backend Team | User management logic |

---

## Knowledge Sources

### Team Wisdom

| Topic | Location | Type | Description |
|-------|----------|------|-------------|
| Onboarding Guide | [NEEDS CREATION] | Wiki/Doc | New developer setup and project overview |
| Troubleshooting FAQ | [NEEDS CREATION] | Wiki/Doc | Common issues and solutions |
| Runbooks | [NEEDS CREATION] | Ops Manual | Incident response and operational procedures |

### Technical Context

| Domain | Resource | Description |
|--------|----------|-------------|
| [Example: GraphQL Best Practices] | [URL or file] | Query optimization and schema design |
| [Example: PostgreSQL Tuning] | [URL or file] | Performance tuning for database layer |

---

## Using the System Map

### For Planning (`/speckit.plan`)

1. **Identify Touched Components**: Cross-reference feature requirements with the Architecture & Design section.
2. **Flag Gaps**: If a touched component has status "⚠️ Missing", add a Bootstrapping Task to Phase N.
3. **Extract Context**: Include relevant artifacts in the "Relevant System Context" section of `plan.md`.

### For Task Generation (`/speckit.tasks`)

1. **Bind Context to Tasks**: For tasks touching specific modules, append `(Ref: <location>)` to task descriptions.
2. **Verify Prerequisites**: Check the Configuration & Infrastructure section for setup requirements.

### For Implementation (`/speckit.implement`)

1. **Follow Standards**: Reference the Code Style Guide and Development Guidelines.
2. **Check Decisions**: Review related ADRs before making architectural changes.

---

## Maintenance Protocol

### When a Feature is Completed

1. **Update Status**: Change artifact status from "⚠️ Missing" to "✅ Active".
2. **Record Location**: Fill in the actual file path or URL.
3. **Update Timestamp**: Set "Last Updated" to the current date.
4. **Add Description**: Briefly describe what the artifact contains.

### When an Artifact is Deprecated

1. **Change Status**: Mark as "🗑️ Deprecated".
2. **Add Reason**: Note why it was deprecated and what replaced it.
3. **Archive**: Move to an `archive/` directory if still needed for reference.

---

## Bootstrap Checklist

If this System Map shows many "⚠️ Missing" artifacts, prioritize creating:

- [ ] **System Architecture Diagram**: Essential for understanding component boundaries.
- [ ] **Database Schema**: Critical for data model discussions.
- [ ] **API Design Doc**: Needed for frontend-backend contracts.
- [ ] **ADR Index**: Start capturing architectural decisions immediately.
- [ ] **Test Strategy**: Define quality gates and coverage expectations.

These form the **Minimum Viable Documentation (MVD)** for effective Spec-Driven Development.

---

**Instructions for Agents**:

- **DO** treat this map as the authoritative index of documentation.
- **DO** propose updates to this map when creating or discovering new artifacts.
- **DO** flag missing artifacts during planning phases.
- **DO NOT** assume artifacts exist if not listed here or marked as "⚠️ Missing".
- **DO NOT** create duplicate documentation without updating this index.

---

**Template Version**: 1.0.0  
**Maintained By**: [Team/Owner]  
**Review Frequency**: After each major feature completion
