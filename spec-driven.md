# Specification-Driven Development (SDD)

## The Power Inversion

For decades, code has been king. Specifications served code—they were the scaffolding we built and then discarded once the "real work" of coding began. We wrote PRDs to guide development, created design docs to inform implementation, drew diagrams to visualize architecture. But these were always subordinate to the code itself. Code was truth. Everything else was, at best, good intentions. Code was the source of truth, and as it moved forward, specs rarely kept pace. As the asset (code) and the implementation are one, it's not easy to have a parallel implementation without trying to build from the code.

Spec-Driven Development (SDD) inverts this power structure. Specifications don't serve code—code serves specifications. The Product Requirements Document (PRD) isn't a guide for implementation; it's the source that generates implementation. Technical plans aren't documents that inform coding; they're precise definitions that produce code. This isn't an incremental improvement to how we build software. It's a fundamental rethinking of what drives development.

The gap between specification and implementation has plagued software development since its inception. We've tried to bridge it with better documentation, more detailed requirements, stricter processes. These approaches fail because they accept the gap as inevitable. They try to narrow it but never eliminate it. SDD eliminates the gap by making specifications and their concrete implementation plans born from the specification executable. When specifications and implementation plans generate code, there is no gap—only transformation.

This transformation is now possible because AI can understand and implement complex specifications, and create detailed implementation plans. But raw AI generation without structure produces chaos. SDD provides that structure through specifications and subsequent implementation plans that are precise, complete, and unambiguous enough to generate working systems. The specification becomes the primary artifact. Code becomes its expression (as an implementation from the implementation plan) in a particular language and framework.

In this new world, maintaining software means evolving specifications. The intent of the development team is expressed in natural language ("**intent-driven development**"), design assets, core principles and other guidelines. The **lingua franca** of development moves to a higher level, and code is the last-mile approach.

Debugging means fixing specifications and their implementation plans that generate incorrect code. Refactoring means restructuring for clarity. The entire development workflow reorganizes around specifications as the central source of truth, with implementation plans and code as the continuously regenerated output. Updating apps with new features or creating a new parallel implementation because we are creative beings, means revisiting the specification and creating new implementation plans. This process is therefore a 0 -> 1, (1', ..), 2, 3, N.

The development team focuses in on their creativity, experimentation, their critical thinking.

## The SDD Workflow in Practice

The workflow begins with an idea—often vague and incomplete. Through iterative dialogue with AI, this idea becomes a comprehensive PRD. The AI asks clarifying questions, identifies edge cases, and helps define precise acceptance criteria. What might take days of meetings and documentation in traditional development happens in hours of focused specification work. This transforms the traditional SDLC—requirements and design become continuous activities rather than discrete phases. This is supportive of a **team process**, where team-reviewed specifications are expressed and versioned, created in branches, and merged.

When a product manager updates acceptance criteria, implementation plans automatically flag affected technical decisions. When an architect discovers a better pattern, the PRD updates to reflect new possibilities.

Throughout this specification process, research agents gather critical context. They investigate library compatibility, performance benchmarks, and security implications. Organizational constraints are discovered and applied automatically—your company's database standards, authentication requirements, and deployment policies seamlessly integrate into every specification.

From the PRD, AI generates implementation plans that map requirements to technical decisions. Every technology choice has documented rationale. Every architectural decision traces back to specific requirements. Throughout this process, consistency validation continuously improves quality. AI analyzes specifications for ambiguity, contradictions, and gaps—not as a one-time gate, but as an ongoing refinement.

Code generation begins as soon as specifications and their implementation plans are stable enough, but they do not have to be "complete." Early generations might be exploratory—testing whether the specification makes sense in practice. Domain concepts become data models. User stories become API endpoints. Acceptance scenarios become tests. This merges development and testing through specification—test scenarios aren't written after code, they're part of the specification that generates both implementation and tests.

The feedback loop extends beyond initial development. Production metrics and incidents don't just trigger hotfixes—they update specifications for the next regeneration. Performance bottlenecks become new non-functional requirements. Security vulnerabilities become constraints that affect all future generations. This iterative dance between specification, implementation, and operational reality is where true understanding emerges and where the traditional SDLC transforms into a continuous evolution.

## Why SDD Matters Now

Three trends make SDD not just possible but necessary:

First, AI capabilities have reached a threshold where natural language specifications can reliably generate working code. This isn't about replacing developers—it's about amplifying their effectiveness by automating the mechanical translation from specification to implementation. It can amplify exploration and creativity, support "start-over" easily, and support addition, subtraction, and critical thinking.

Second, software complexity continues to grow exponentially. Modern systems integrate dozens of services, frameworks, and dependencies. Keeping all these pieces aligned with original intent through manual processes becomes increasingly difficult. SDD provides systematic alignment through specification-driven generation. Frameworks may evolve to provide AI-first support, not human-first support, or architect around reusable components.

Third, the pace of change accelerates. Requirements change far more rapidly today than ever before. Pivoting is no longer exceptional—it's expected. Modern product development demands rapid iteration based on user feedback, market conditions, and competitive pressures. Traditional development treats these changes as disruptions. Each pivot requires manually propagating changes through documentation, design, and code. The result is either slow, careful updates that limit velocity, or fast, reckless changes that accumulate technical debt.

SDD can support what-if/simulation experiments: "If we need to re-implement or change the application to promote a business need to sell more T-shirts, how would we implement and experiment for that?"

SDD transforms requirement changes from obstacles into normal workflow. When specifications drive implementation, pivots become systematic regenerations rather than manual rewrites. Change a core requirement in the PRD, and affected implementation plans update automatically. Modify a user story, and corresponding API endpoints regenerate. This isn't just about initial development—it's about maintaining engineering velocity through inevitable changes.

## Core Principles

**Specifications as the Lingua Franca**: The specification becomes the primary artifact. Code becomes its expression in a particular language and framework. Maintaining software means evolving specifications.

**Executable Specifications**: Specifications must be precise, complete, and unambiguous enough to generate working systems. This eliminates the gap between intent and implementation.

**Continuous Refinement**: Consistency validation happens continuously, not as a one-time gate. AI analyzes specifications for ambiguity, contradictions, and gaps as an ongoing process.

**Research-Driven Context**: Research agents gather critical context throughout the specification process, investigating technical options, performance implications, and organizational constraints.

**Bidirectional Feedback**: Production reality informs specification evolution. Metrics, incidents, and operational learnings become inputs for specification refinement.

**Branching for Exploration**: Generate multiple implementation approaches from the same specification to explore different optimization targets—performance, maintainability, user experience, cost.

**Skills-First**: When a skill exists for a task, it must be used. Skill personas (architect, developer, tech-lead, librarian) are invoked by phase and override general AI behavior, providing consistent, expert-level guidance throughout the lifecycle.

**Documentation Continuity**: Documentation is never an afterthought. The System Map (`memory/system-map.md`) tracks every artifact; the Convergence phase (Phase N) closes all documentation gaps before a feature is considered complete.

**Context Awareness**: Each phase narrows its context progressively—System Map → Plan → Tasks → Implementation. This Context Funnel ensures AI agents work with the minimum necessary information at each stage, reducing noise and improving accuracy.

## Implementation Approaches

Today, practicing SDD requires assembling existing tools and maintaining discipline throughout the process. The methodology can be practiced with:

- AI assistants for iterative specification development
- Research agents for gathering technical context
- Code generation tools for translating specifications to implementation
- Version control systems adapted for specification-first workflows
- Consistency checking through AI analysis of specification documents

The key is treating specifications as the source of truth, with code as the generated output that serves the specification rather than the other way around.

## The 6-Phase Lifecycle

Spec-Driven Development in v2 is structured as a six-phase lifecycle. Each phase maps to a `/speckit.*` command that invokes the appropriate AI skill persona:

| Phase | Command | Skill Persona | Description |
|-------|---------|---------------|-------------|
| **Specify** | `/speckit.specify` | — | Create a structured feature specification from a natural-language description |
| **Clarify** | `/speckit.clarify` | — | Ask up to 5 targeted questions to resolve ambiguities before planning (optional) |
| **Plan** | `/speckit.plan` | `speckit-architect` | Design architecture, ADRs, data models, API contracts, and Documentation State Matrix |
| **Task** | `/speckit.tasks` | `speckit-tech-lead`, `speckit-developer` | Generate dependency-ordered tasks split by `<!-- CONVERGENCE_BOUNDARY -->` |
| **Implement** | `/speckit.implement` | `speckit-developer` | Execute Phases 1 through N-1; hard stop at CONVERGENCE_BOUNDARY |
| **Converge** | `/speckit.converge` | `speckit-librarian` | Phase N — update ADRs, System Map, close documentation gaps |

**Additional commands:**

| Command | Purpose |
|---------|---------|
| `/speckit.constitution` | Establish project principles and governance (run once at project start) |
| `/speckit.analyze` | Cross-artifact consistency check — run after tasks, before implement |
| `/speckit.checklist` | Generate quality checklists for requirements validation |
| `/speckit.taskstoissues` | Convert tasks into GitHub issues for team collaboration |
| `/speckit.doc-update` | Manage project documentation in sync with `memory/system-map.md` — standalone utility, lifecycle-independent, invocable at any time |

### The CONVERGENCE_BOUNDARY

Tasks generated by `/speckit.tasks` are split into two groups by a `<!-- CONVERGENCE_BOUNDARY -->` marker in `tasks.md`:

- **Phases 1 through N-1** — Implementation tasks executed by `/speckit.implement`. The implement command enforces a **hard stop** at this marker.
- **Phase N (System Convergence)** — Documentation tasks executed only by `/speckit.converge`. These include updating ADRs, synchronizing the System Map, and closing every gap identified in the plan's Documentation State Matrix.

This separation ensures documentation convergence is a first-class, non-skippable step rather than an afterthought.

## Streamlining SDD with Commands

The SDD methodology is significantly enhanced through commands that automate the full specification → planning → tasking → implementation → convergence workflow:

### The `/speckit.specify` Command

This command transforms a simple feature description (the user-prompt) into a complete, structured specification with automatic repository management:

1. **Automatic Feature Numbering**: Scans existing specs to determine the next feature number (e.g., 001, 002, 003)
2. **Branch Creation**: Generates a typed, semantic branch name from your description (e.g., `feat/003-chat-system`) and creates it automatically
3. **Template-Based Generation**: Copies and customizes the feature specification template with your requirements
4. **Directory Structure**: Creates the proper `specs/[feature-number]-[name]/` structure for all related documents

> **Branch naming (v2.1+):** Branches follow the `type/###-name` format with six supported types: `feat`, `bug`, `hotfix`, `refactor`, `docs`, `chore`. Use the `--type` flag (bash) or `-Type` (PowerShell) when creating a new feature. The specs directory always uses the flat `###-name` format without the type prefix.

### The `/speckit.clarify` Command (Optional)

Before creating a plan, this command scans the active specification for underspecified areas and asks up to 5 high-impact clarification questions:

1. **Ambiguity Scan**: Analyzes the spec across functional scope, data model, UX flows, non-functional attributes, and integration concerns
2. **Targeted Questions**: Produces the highest-priority questions only — avoids over-asking
3. **Spec Update**: Encodes the user's answers directly back into the spec file, reducing downstream rework

This step is recommended but optional. Skipping it increases the risk of rework during the Plan and Implement phases.

### The `/speckit.plan` Command

Once a feature specification exists, this command creates a comprehensive implementation plan:

1. **Specification Analysis**: Reads and understands the feature requirements, user stories, and acceptance criteria
2. **Constitutional Compliance**: Ensures alignment with project constitution and architectural principles
3. **Technical Translation**: Converts business requirements into technical architecture and implementation details
4. **Detailed Documentation**: Generates supporting documents for data models, API contracts, and test scenarios
5. **System Map Integration**: Reads `memory/system-map.md` to identify touched components and registers new artifacts
6. **Documentation State Matrix**: Tracks which documents need to be created, updated, or verified during Convergence
7. **Gap Analysis**: Flags missing artifacts that must be bootstrapped in Phase N

### The `/speckit.tasks` Command

After a plan is created, this command analyzes the plan and related design documents to generate an executable task list:

1. **Inputs**: Reads `plan.md` (required) and, if present, `data-model.md`, `contracts/`, and `research.md`
2. **Task Derivation**: Converts contracts, entities, and scenarios into specific tasks
3. **Parallelization**: Marks independent tasks `[P]` and outlines safe parallel groups
4. **CONVERGENCE_BOUNDARY**: Inserts the `<!-- CONVERGENCE_BOUNDARY -->` marker between implementation phases (1 through N-1) and the final documentation convergence phase (Phase N)
5. **Output**: Writes `tasks.md` in the feature directory, ready for execution

### The `/speckit.implement` Command

This command executes all implementation tasks defined in `tasks.md`:

1. **Skills Loading**: Runs `resolve-skills.sh implement` to load the `speckit-developer` persona for this phase
2. **Checklist Gate**: If checklists exist in `checklists/`, verifies they are all passing before proceeding
3. **Context Loading**: Reads `tasks.md`, `plan.md`, and supporting documents (`data-model.md`, `contracts/`, etc.)
4. **Task Execution**: Works through tasks in dependency order, following TDD — tests before implementation code
5. **Hard Stop**: Halts at `<!-- CONVERGENCE_BOUNDARY -->` and hands off to `/speckit.converge`

### The `/speckit.converge` Command

The final phase closes all documentation gaps and synchronizes project memory:

1. **Skills Loading**: Runs `resolve-skills.sh converge` to load the `speckit-librarian` persona
2. **Pre-condition Check**: Verifies all implementation tasks (above the CONVERGENCE_BOUNDARY) are complete; stops if not
3. **Convergence Context**: Reads `plan.md` (Documentation State Matrix, Gap Analysis) and `memory/system-map.md`
4. **Phase N Execution**: Creates/updates ADRs, updates architecture docs, synchronizes the System Map, and closes every flagged gap
5. **Validation**: Confirms every entry in the Documentation State Matrix has been addressed

### Example: Building a Chat Feature

Here's how these commands transform the traditional development workflow:

**Traditional Approach:**

```text
1. Write a PRD in a document (2-3 hours)
2. Create design documents (2-3 hours)
3. Set up project structure manually (30 minutes)
4. Write technical specifications (3-4 hours)
5. Create test plans (2 hours)
Total: ~12 hours of documentation work
```

**SDD with Commands Approach:**

```bash
# Step 1: Create the feature specification (5 minutes)
/speckit.specify Real-time chat system with message history and user presence

# This automatically:
# - Creates branch "feat/003-chat-system"
# - Generates specs/003-chat-system/spec.md
# - Populates it with structured requirements

# Step 1b: (Optional) Clarify ambiguous areas before planning
/speckit.clarify

# Step 2: Generate implementation plan (5 minutes)
/speckit.plan WebSocket for real-time messaging, PostgreSQL for history, Redis for presence

# This automatically creates:
# - specs/003-chat-system/plan.md (with Documentation State Matrix + Gap Analysis)
# - specs/003-chat-system/research.md (WebSocket library comparisons)
# - specs/003-chat-system/data-model.md (Message and User schemas)
# - specs/003-chat-system/contracts/ (WebSocket events, REST endpoints)
# - specs/003-chat-system/quickstart.md (Key validation scenarios)

# Step 3: Generate executable tasks (5 minutes)
/speckit.tasks

# This automatically creates:
# - specs/003-chat-system/tasks.md
#   (phases 1–N-1 above the CONVERGENCE_BOUNDARY, Phase N below)

# Step 4: Execute implementation (time varies)
/speckit.implement

# Runs all tasks up to CONVERGENCE_BOUNDARY following TDD;
# halts and prompts for /speckit.converge when done.

# Step 5: Converge documentation (5-10 minutes)
/speckit.converge

# Executes Phase N tasks: updates ADRs, syncs system-map.md,
# closes every gap flagged in plan.md
```

In ~30 minutes of specification and planning work, plus focused implementation, you have:

- A complete feature specification with user stories and acceptance criteria
- A detailed implementation plan with technology choices and rationale
- API contracts and data models ready for code generation
- Comprehensive test scenarios — written before implementation code
- All documents properly versioned in a typed feature branch
- A fully synchronized System Map and closed documentation gaps

### The Power of Structured Automation

These commands don't just save time—they enforce consistency and completeness:

1. **No Forgotten Details**: Templates ensure every aspect is considered, from non-functional requirements to error handling
2. **Traceable Decisions**: Every technical choice links back to specific requirements
3. **Living Documentation**: Specifications stay in sync with code because they generate it — and Convergence enforces this
4. **Rapid Iteration**: Change requirements and regenerate plans in minutes, not days
5. **Phase Separation**: The CONVERGENCE_BOUNDARY guarantees documentation convergence is never skipped

The commands embody SDD principles by treating specifications as executable artifacts rather than static documents. They transform the specification process from a necessary evil into the driving force of development.

### Template-Driven Quality: How Structure Constrains LLMs for Better Outcomes

The true power of these commands lies not just in automation, but in how the templates guide LLM behavior toward higher-quality specifications. The templates act as sophisticated prompts that constrain the LLM's output in productive ways:

#### 1. **Preventing Premature Implementation Details**

The feature specification template explicitly instructs:

```text
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
```

This constraint forces the LLM to maintain proper abstraction levels. When an LLM might naturally jump to "implement using React with Redux," the template keeps it focused on "users need real-time updates of their data." This separation ensures specifications remain stable even as implementation technologies change.

#### 2. **Forcing Explicit Uncertainty Markers**

Both templates mandate the use of `[NEEDS CLARIFICATION]` markers:

```text
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question]
2. **Don't guess**: If the prompt doesn't specify something, mark it
```

This prevents the common LLM behavior of making plausible but potentially incorrect assumptions. Instead of guessing that a "login system" uses email/password authentication, the LLM must mark it as `[NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]`.

#### 3. **Structured Thinking Through Checklists**

The templates include comprehensive checklists that act as "unit tests" for the specification:

```markdown
### Requirement Completeness

- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
```

These checklists force the LLM to self-review its output systematically, catching gaps that might otherwise slip through. It's like giving the LLM a quality assurance framework.

#### 4. **Constitutional Compliance Through Gates**

The implementation plan template enforces architectural principles through phase gates:

```markdown
### Phase -1: Pre-Implementation Gates

#### Simplicity Gate (Article VII)

- [ ] Using ≤3 projects?
- [ ] No future-proofing?

#### Anti-Abstraction Gate (Article VIII)

- [ ] Using framework directly?
- [ ] Single model representation?
```

These gates prevent over-engineering by making the LLM explicitly justify any complexity. If a gate fails, the LLM must document why in the "Complexity Tracking" section, creating accountability for architectural decisions.

#### 5. **Hierarchical Detail Management**

The templates enforce proper information architecture:

```text
**IMPORTANT**: This implementation plan should remain high-level and readable.
Any code samples, detailed algorithms, or extensive technical specifications
must be placed in the appropriate `implementation-details/` file
```

This prevents the common problem of specifications becoming unreadable code dumps. The LLM learns to maintain appropriate detail levels, extracting complexity to separate files while keeping the main document navigable.

#### 6. **Test-First Thinking**

The implementation template enforces test-first development:

```text
### File Creation Order
1. Create `contracts/` with API specifications
2. Create test files in order: contract → integration → e2e → unit
3. Create source files to make tests pass
```

This ordering constraint ensures the LLM thinks about testability and contracts before implementation, leading to more robust and verifiable specifications.

#### 7. **Preventing Speculative Features**

Templates explicitly discourage speculation:

```text
- [ ] No speculative or "might need" features
- [ ] All phases have clear prerequisites and deliverables
```

This stops the LLM from adding "nice to have" features that complicate implementation. Every feature must trace back to a concrete user story with clear acceptance criteria.

### The Compound Effect

These constraints work together to produce specifications that are:

- **Complete**: Checklists ensure nothing is forgotten
- **Unambiguous**: Forced clarification markers highlight uncertainties
- **Testable**: Test-first thinking baked into the process
- **Maintainable**: Proper abstraction levels and information hierarchy
- **Implementable**: Clear phases with concrete deliverables

The templates transform the LLM from a creative writer into a disciplined specification engineer, channeling its capabilities toward producing consistently high-quality, executable specifications that truly drive development.

## The Constitutional Foundation: Enforcing Architectural Discipline

At the heart of SDD lies a constitution—a set of immutable principles that govern how specifications become code. The constitution (`memory/constitution.md`) acts as the architectural DNA of the system, ensuring that every generated implementation maintains consistency, simplicity, and quality. Constitution v2.0.0 defines nine articles and the full 6-phase lifecycle.

### The Nine Articles of Development

The constitution defines nine articles that shape every aspect of the development process:

#### Article I: Library-First Principle

Every feature must begin as a standalone library—no exceptions. This forces modular design from the start:

```text
Every feature in Specify MUST begin its existence as a standalone library.
No feature shall be implemented directly within application code without
first being abstracted into a reusable library component.
```

This principle ensures that specifications generate modular, reusable code rather than monolithic applications. When the LLM generates an implementation plan, it must structure features as libraries with clear boundaries and minimal dependencies.

#### Article II: CLI Interface Mandate

Every library must expose its functionality through a command-line interface:

```text
All CLI interfaces MUST:
- Accept text as input (via stdin, arguments, or files)
- Produce text as output (via stdout)
- Support JSON format for structured data exchange
```

This enforces observability and testability. The LLM cannot hide functionality inside opaque classes—everything must be accessible and verifiable through text-based interfaces.

#### Article III: Test-First Imperative

The most transformative article—no code before tests:

```text
This is NON-NEGOTIABLE: All implementation MUST follow strict Test-Driven Development.
No implementation code shall be written before:
1. Unit tests are written
2. Tests are validated and approved by the user
3. Tests are confirmed to FAIL (Red phase)
```

This completely inverts traditional AI code generation. Instead of generating code and hoping it works, the LLM must first generate comprehensive tests that define behavior, get them approved, and only then generate implementation.

#### Articles VII & VIII: Simplicity and Anti-Abstraction

These paired articles combat over-engineering:

```text
Section 7.3: Minimal Project Structure
- Maximum 3 projects for initial implementation
- Additional projects require documented justification

Section 8.1: Framework Trust
- Use framework features directly rather than wrapping them
```

When an LLM might naturally create elaborate abstractions, these articles force it to justify every layer of complexity. The implementation plan template's "Phase -1 Gates" directly enforce these principles.

#### Article IX: Integration-First Testing

Prioritizes real-world testing over isolated unit tests:

```text
Tests MUST use realistic environments:
- Prefer real databases over mocks
- Use actual service instances over stubs
- Contract tests mandatory before implementation
```

This ensures generated code works in practice, not just in theory.

### Constitutional Enforcement Through Templates

The implementation plan template operationalizes these articles through concrete checkpoints:

```markdown
### Phase -1: Pre-Implementation Gates

#### Simplicity Gate (Article VII)

- [ ] Using ≤3 projects?
- [ ] No future-proofing?

#### Anti-Abstraction Gate (Article VIII)

- [ ] Using framework directly?
- [ ] Single model representation?

#### Integration-First Gate (Article IX)

- [ ] Contracts defined?
- [ ] Contract tests written?
```

These gates act as compile-time checks for architectural principles. The LLM cannot proceed without either passing the gates or documenting justified exceptions in the "Complexity Tracking" section.

### The Power of Immutable Principles

The constitution's power lies in its immutability. While implementation details can evolve, the core principles remain constant. This provides:

1. **Consistency Across Time**: Code generated today follows the same principles as code generated next year
2. **Consistency Across LLMs**: Different AI models produce architecturally compatible code
3. **Architectural Integrity**: Every feature reinforces rather than undermines the system design
4. **Quality Guarantees**: Test-first, library-first, and simplicity principles ensure maintainable code

### Constitutional Evolution

While principles are immutable, their application can evolve:

```text
Section 4.2: Amendment Process
Modifications to this constitution require:
- Explicit documentation of the rationale for change
- Review and approval by project maintainers
- Backwards compatibility assessment
```

This allows the methodology to learn and improve while maintaining stability. The constitution shows its own evolution with dated amendments, demonstrating how principles can be refined based on real-world experience.

### Beyond Rules: A Development Philosophy

The constitution isn't just a rulebook—it's a philosophy that shapes how LLMs think about code generation:

- **Observability Over Opacity**: Everything must be inspectable through CLI interfaces
- **Simplicity Over Cleverness**: Start simple, add complexity only when proven necessary
- **Integration Over Isolation**: Test in real environments, not artificial ones
- **Modularity Over Monoliths**: Every feature is a library with clear boundaries

By embedding these principles into the specification and planning process, SDD ensures that generated code isn't just functional—it's maintainable, testable, and architecturally sound. The constitution transforms AI from a code generator into an architectural partner that respects and reinforces system design principles.

## Skills Architecture

Spec Kit v2 introduces a **Skills Architecture** that gives AI agents phase-specific expertise through dedicated skill personas. Each skill follows the **Adapter Pattern**: a portable `SKILL.md` defines the core persona, while a `speckit-adapter.yaml` sidecar handles SpecKit-specific integration.

### Core Skill Personas

| Skill | Phase | Role |
|-------|-------|------|
| `speckit-architect` | Plan | High-level design, ADRs, gap analysis, Documentation State Matrix |
| `speckit-tech-lead` | Task | Task planning, dependency management, phase structure |
| `speckit-developer` | Implement, Task | TDD enforcement, clean code, contract-first development |
| `speckit-librarian` | Converge | Documentation convergence, System Map synchronization |

### How Skills Are Resolved

The `scripts/bash/resolve-skills.sh` (Linux/macOS) and `scripts/powershell/resolve-skills.ps1` (Windows) scripts are invoked automatically by each phase command. They:

1. Reads `.speckit.yaml` (if present) to discover skill scan directories
2. Scans for skills that match the current lifecycle phase via `speckit-adapter.yaml` hooks
3. Sorts matched skills by priority
4. Injects the skill content and instructions into the AI agent's context

Skills are **mandatory** — when a skill is loaded for a phase, the AI agent must adopt its persona and follow all workflow steps it defines. Skills override general training behavior.

### The Adapter Pattern

```yaml
# Example: skills/speckit-architect/speckit-adapter.yaml
name: speckit-architect
hooks:
  - phase: plan
    priority: 100
    context: SKILL.md
    instructions: |
      ## SpecKit Integration
      - Read memory/system-map.md to identify touched components
      - Add Documentation State Matrix entries to plan.md
```

The `SKILL.md` file contains the portable persona definition with no SpecKit-specific paths, making skills reusable across different projects. The adapter sidecar wires the skill into the SpecKit workflow.

## Project Configuration (`.speckit.yaml`)

An optional `.speckit.yaml` file at the project root allows teams to customize the Spec Kit behavior:

```yaml
version: "2.0.0"
skills:
  scan_dirs:
    - skills/           # project-level skills
    - .specify/skills/  # specify-local skills
    - .github/skills/   # Copilot-specific skills
memory:
  system_map: .specify/memory/system-map.md
  constitution: .specify/memory/constitution.md
```

**Key configuration options:**

- **`skills.scan_dirs`**: List of directories scanned for skill definitions. Skills in later directories supplement (not replace) earlier ones.
- **`memory.system_map`**: Path to the System Map document that tracks all project artifacts.
- **`memory.constitution`**: Path to the project constitution governing all development decisions.

When `.speckit.yaml` is absent, Spec Kit uses sensible defaults and scans the standard skill directories for the active AI agent.

## The Transformation

This isn't about replacing developers or automating creativity. It's about amplifying human capability by automating mechanical translation. It's about creating a tight feedback loop where specifications, research, and code evolve together, each iteration bringing deeper understanding and better alignment between intent and implementation.

Software development needs better tools for maintaining alignment between intent and implementation. SDD provides the methodology for achieving this alignment through executable specifications that generate code rather than merely guiding it.
