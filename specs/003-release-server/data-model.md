# Data Model: Release Server

## Entities

### Package (File)

Represents a stored artifact on the filesystem.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The filename (e.g., `spec-kit-template-claude-sh.zip`). Unique ID. |
| `path` | string | Internal filesystem path (`/data/{name}`). |
| `size` | integer | Size in bytes. |
| `created_at` | datetime | Creation timestamp (mtime). |
| `url` | string | Public download URL. |

## Data Storage

*   **Persistence**: Filesystem.
*   **Location**: `/data` (Configurable).
*   **Config**: `CONFIG_PATH` (Env var) pointing to YAML, or direct Env vars.
*   **Auth**: `AUTH_TOKEN` (Env var) for write protection.
*   **Indexing**: memory/on-the-fly directory listing (due to low scale).

## Validation Rules

1.  **Unique Filename**: By default, upload fails if file exists. Overwrite allowed via flag.
2.  **Retention Policy**: Total count of files <= `MAX_PACKAGES` (Global limit).

## API Schemas

### GitHubRelease (Response)
Schema for `GET /latest` to ensure compatibility with `specify` CLI.

```json
{
  "tag_name": "latest",
  "name": "Latest Release",
  "assets": [
    {
      "name": "string",
      "size": "integer",
      "browser_download_url": "string (URL)"
    }
  ]
}
```

### PackageMetadata (Internal/List)
Schema for `GET /packages` (JSON format).

```json
[
  {
    "filename": "string",
    "size": "integer",
    "uploaded_at": "string (ISO 8601)",
    "download_url": "string (URL)"
  }
]
```
