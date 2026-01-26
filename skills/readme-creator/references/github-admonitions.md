# GitHub Admonitions (Alerts) Guide

Complete guide to using GitHub's alert/admonition syntax in Markdown.

## Overview

GitHub supports special blockquote syntax for creating styled alerts (also known as admonitions or callouts). These provide distinctive styling for important, noteworthy, or warning content.

**Feature Status**: Released December 14, 2023  
**Documentation**: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts

## Syntax

Alerts use a special blockquote format:

```markdown
> [!TYPE]
> Content goes here
```

The first line must be exactly `> [!TYPE]` where TYPE is one of the supported alert types.  
A line break following the type declaration is **required**.

## Supported Alert Types

GitHub supports five alert types:

### 1. NOTE (Blue)

```markdown
> [!NOTE]
> Highlights information that users should take into account, even when skimming.
```

**Renders as**:

> [!NOTE]
> Highlights information that users should take into account, even when skimming.

**Use for**:
- Supplemental information
- Context that helps understanding
- Things users should be aware of
- Background information

### 2. TIP (Green)

```markdown
> [!TIP]
> Optional information to help a user be more successful.
```

**Renders as**:

> [!TIP]
> Optional information to help a user be more successful.

**Use for**:
- Helpful suggestions
- Best practices
- Performance tips
- Shortcuts or time-savers

### 3. IMPORTANT (Purple)

```markdown
> [!IMPORTANT]
> Crucial information necessary for users to succeed.
```

**Renders as**:

> [!IMPORTANT]
> Crucial information necessary for users to succeed.

**Use for**:
- Critical steps
- Required actions
- Key decisions
- Must-know information

### 4. WARNING (Yellow/Orange)

```markdown
> [!WARNING]
> Critical content demanding immediate user attention due to potential risks.
```

**Renders as**:

> [!WARNING]
> Critical content demanding immediate user attention due to potential risks.

**Use for**:
- Potential problems
- Breaking changes
- Deprecated features
- Actions that may have negative consequences

### 5. CAUTION (Red)

```markdown
> [!CAUTION]
> Negative potential consequences of an action.
```

**Renders as**:

> [!CAUTION]
> Negative potential consequences of an action.

**Use for**:
- Dangerous operations
- Data loss risks
- Security concerns
- Irreversible actions

## Alert Severity Hierarchy

From least to most severe:

1. **NOTE** (Blue) - Informational
2. **TIP** (Green) - Helpful
3. **IMPORTANT** (Purple) - Required
4. **WARNING** (Orange) - Proceed with care
5. **CAUTION** (Red) - Danger

## Multi-Line Alerts

Alerts can contain multiple paragraphs and other Markdown elements:

```markdown
> [!NOTE]
> This alert has multiple paragraphs.
> 
> You can include:
> - Lists
> - `Code snippets`
> - **Bold text**
> - Links and more
```

**Renders as**:

> [!NOTE]
> This alert has multiple paragraphs.
> 
> You can include:
> - Lists
> - `Code snippets`
> - **Bold text**
> - Links and more

## Supported Content Within Alerts

Alerts support most Markdown features:

### Text Formatting

```markdown
> [!TIP]
> You can use **bold**, _italic_, and `code` formatting within alerts.
```

### Lists

```markdown
> [!IMPORTANT]
> Make sure to:
> - Install dependencies
> - Configure environment
> - Run tests
```

### Code Blocks

```markdown
> [!NOTE]
> Example usage:
> ```bash
> npm install
> npm start
> ```
```

### Links

```markdown
> [!WARNING]
> See the [security guide](docs/security.md) before proceeding.
```

### Inline Code

```markdown
> [!TIP]
> Use the `--force` flag to override checks.
```

## Limitations and Constraints

### Cannot Be Nested

Alerts **cannot** be nested inside other block elements:

❌ **Does not work** - nested in lists:
```markdown
1. First step
   > [!NOTE]
   > This won't render as an alert
```

❌ **Does not work** - nested in blockquotes:
```markdown
> Regular quote
> > [!NOTE]
> > This won't render as an alert
```

❌ **Does not work** - nested in `<details>`:
```markdown
<details>
<summary>Click to expand</summary>

> [!NOTE]
> This won't render as an alert

</details>
```

### Must Be Top-Level

Alerts must be at the top level of the document or section, not indented or nested.

### Line Break Required

A line break after the alert type is **required**:

✅ **Correct**:
```markdown
> [!NOTE]
> Content here
```

❌ **Incorrect**:
```markdown
> [!NOTE] Content here
```

### Case Sensitive

The alert type must be in UPPERCASE:

✅ **Correct**: `[!NOTE]`, `[!WARNING]`  
❌ **Incorrect**: `[!note]`, `[!Warning]`

### English Only

Alert types are English-only keywords. The labels displayed ("Note", "Tip", etc.) are also in English and cannot be customized.

## Where Alerts Work

Alerts are supported in:

- ✅ README.md files
- ✅ Markdown documentation files
- ✅ Issue comments
- ✅ Pull request comments
- ✅ Discussion comments
- ✅ Wiki pages
- ❌ GitHub Pages (requires third-party plugins)
- ❌ Generic Markdown renderers (CommonMark, etc.)

## Common Use Cases

### Installation Prerequisites

```markdown
> [!IMPORTANT]
> You must have Node.js version 18 or higher installed before proceeding.
```

### Version-Specific Notes

```markdown
> [!NOTE]
> You can test this application locally without any cost using [Ollama](https://ollama.com/).
```

### Breaking Changes

```markdown
> [!WARNING]
> Version 2.0 introduces breaking changes. See the [migration guide](MIGRATION.md) before upgrading.
```

### Security Warnings

```markdown
> [!CAUTION]
> Never commit API keys or secrets to your repository. Use environment variables instead.
```

### Performance Tips

```markdown
> [!TIP]
> For large datasets, consider enabling caching to improve performance.
```

### Configuration Requirements

```markdown
> [!IMPORTANT]
> Ensure your `.env` file is properly configured before running the application.
```

## Best Practices

### Do's ✅

1. **Use sparingly**: Too many alerts reduce their impact
2. **Choose appropriate severity**: Match the alert type to the content importance
3. **Be concise**: Keep alert content brief and to the point
4. **Use for key information**: Reserve for truly important/helpful content
5. **Combine with other formatting**: Use lists, code, links within alerts

### Don'ts ❌

1. **Don't overuse**: Limit to 1-3 alerts per section
2. **Don't nest**: Alerts don't work when nested in other elements
3. **Don't use for decoration**: Use only when content truly needs highlighting
4. **Don't duplicate headings**: Alerts complement, don't replace headings
5. **Don't use all caps content**: The alert itself provides emphasis

## Examples in Context

### README Example

```markdown
# My Project

Brief project description.

## Installation

> [!IMPORTANT]
> Requires Node.js 18+ and npm 9+

Install the package:

\```bash
npm install my-project
\```

> [!TIP]
> For development, use `npm link` to test local changes.

## Configuration

> [!WARNING]
> The default configuration is not suitable for production use.

Create a `.env` file with your settings...
```

### Documentation Example

```markdown
## API Authentication

> [!CAUTION]
> API keys provide full access to your account. Never share them publicly.

To authenticate, include your API key in the header:

\```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.example.com
\```

> [!NOTE]
> API keys can be generated from your account dashboard.
```

## Compatibility Notes

### GitHub-Specific

This syntax is **GitHub-specific** (GitHub Flavored Markdown). It will not work in:
- Standard CommonMark renderers
- GitLab Flavored Markdown (uses different syntax)
- Generic Markdown parsers
- Most static site generators (without plugins)

### Alternative Syntaxes

Other platforms use different syntax for admonitions:

**Obsidian**:
```markdown
> [!note] Optional Title
> Content here
```

**Docusaurus/VuePress** (CommonMark directives):
```markdown
:::note
Content here
:::
```

**Microsoft Docs**:
```markdown
> [!NOTE]
> Content here
```
(Similar but different implementation)

## History and Updates

- **May 19, 2022**: Initial beta announcement
- **July 21, 2023**: Added `[!NOTE]` syntax, replaced old `**Note**` syntax
- **October 12, 2023**: Bug fixes for Wikis and nested blockquotes
- **November 14, 2023**: Added `[!TIP]` and `[!CAUTION]`, prevented nesting
- **December 14, 2023**: Official release with full documentation

## Migration from Old Syntax

The old syntax using `**Note**` is **no longer supported**:

❌ **Old** (deprecated):
```markdown
> **Note**
> This is a note
```

✅ **New** (current):
```markdown
> [!NOTE]
> This is a note
```

## Troubleshooting

### Alert Not Rendering

Check for these common issues:

1. **Missing line break**: Ensure there's a line break after `[!TYPE]`
2. **Incorrect case**: Type must be uppercase (`[!NOTE]`, not `[!note]`)
3. **Nested element**: Alerts don't work inside lists, blockquotes, etc.
4. **Wrong environment**: Alerts only work on GitHub, not all Markdown renderers
5. **Typo in type**: Must be exactly one of: NOTE, TIP, IMPORTANT, WARNING, CAUTION

### Not Showing in Preview

If alerts don't show in VS Code or other editors:
- This is expected - alerts are GitHub-specific
- Preview will show them as regular blockquotes
- They will render correctly on GitHub

### Styling Issues

If styling seems wrong:
- Clear browser cache
- Check if viewing on github.com (not third-party sites)
- Verify syntax is exactly correct

## Resources

- **Official Documentation**: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#alerts
- **Changelog**: https://github.blog/changelog/2023-12-14-new-markdown-extension-alerts-provide-distinctive-styling-for-significant-content/
- **Community Discussion**: https://github.com/orgs/community/discussions/16925

## Summary

GitHub alerts provide a powerful way to highlight important information in your documentation. Use them wisely:

- **NOTE**: General information worth noting
- **TIP**: Helpful suggestions
- **IMPORTANT**: Critical for success
- **WARNING**: Potential risks
- **CAUTION**: Serious dangers

Remember: These work only on GitHub. For cross-platform documentation, consider alternative approaches or use conditional rendering.
