---
name: readme-creator
description: Create comprehensive, professional README.md files for software projects. Use when users want to (1) create a new README from scratch, (2) improve or rewrite an existing README, (3) add specific sections like badges, installation, or usage examples, or (4) follow best practices for GitHub project documentation.
---

# README Creator

Create professional README.md files that are appealing, informative, and easy to read.

## Workflow

1. **Analyze the project** - Review workspace to identify: project type, key features, target audience, available logo/screenshots
2. **Select structure** - Choose sections based on project complexity (see Structure below)
3. **Write content** - Start with title/description, then Getting Started, then remaining sections
4. **Add visuals** - Logo, badges, screenshots/GIFs where helpful
5. **Validate** - Check links, test code examples, preview rendering

## Structure

### Required Sections

| Section | Content |
|---------|---------|
| **Title + Description** | Name, tagline, 2-3 sentence description, badges |
| **Getting Started** | Prerequisites, installation, quick example |
| **License** | Brief mention with link to LICENSE file |

### Optional Sections (add as needed)

- **Features** - Key capabilities with bullet points
- **Usage** - Examples, CLI commands, API reference
- **Resources** - Links to docs, tutorials, related projects
- **Contributing** - Brief note linking to CONTRIBUTING.md
- **Support** - How to get help, community links

### Sections to AVOID

Do NOT include full content for: LICENSE, CONTRIBUTING, CHANGELOG, CODE_OF_CONDUCT (use separate files).

## Key Patterns

### Header with Logo

```html
<div align="center">
  <img src="./logo.png" alt="Logo" height="64" />
  <h1>Project Name</h1>
  <p>One-line description</p>
  
  [![Build](badge-url)](link) [![License](badge-url)](LICENSE)
  
  [Overview](#overview) • [Install](#installation) • [Usage](#usage)
</div>
```

### GitHub Admonitions

```markdown
> [!NOTE]
> Informational highlight

> [!TIP]
> Helpful suggestion

> [!IMPORTANT]
> Critical requirement

> [!WARNING]
> Potential risk

> [!CAUTION]
> Dangerous action
```

See [references/github-admonitions.md](references/github-admonitions.md) for full syntax guide.

### Collapsible Getting Started Options

```markdown
<details open>
<summary><h3>GitHub Codespaces</h3></summary>

[![Open in Codespaces](badge)](link)

</details>

<details>
<summary><h3>Local Environment</h3></summary>

Prerequisites and installation steps...

</details>
```

## Guidelines

### Do
- Start with clear, compelling description
- Include working code examples
- Use 3-5 badges max (build, version, license)
- Keep paragraphs to 3-5 lines
- Use admonitions for important notes

### Don't
- Write walls of text
- Use excessive emojis (1-2 per section max)
- Duplicate content from other files
- Include outdated information
- Over-nest sections (3 levels max)

## References

- **Examples**: See [references/readme-examples.md](references/readme-examples.md) for patterns from well-structured READMEs
- **Admonitions**: See [references/github-admonitions.md](references/github-admonitions.md) for GitHub alert syntax
- **Template**: See [references/full-readme-template.md](references/full-readme-template.md) for comprehensive template
