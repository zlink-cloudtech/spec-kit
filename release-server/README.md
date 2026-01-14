# Release Server

A lightweight HTTP server for hosting and distributing `spec-kit` templates.

## Features

- **Package Hosting**: Upload and download release packages via HTTP.
- **GitHub Compatibility**: `/latest` endpoint mimics GitHub Release API for easy integration with `specify init`.
- **Retention Policy**: Automatically cleans up old packages (configurable limit).
- **Web Interface**: Simple HTML listing of available packages at `/packages`.
- **Dockerized**: Ready for container orchestration.

## Quickstart

### Local Development

1. **Install dependencies**:

   ```bash
   pip install -e .[dev]
   ```

2. **Run server**:

   ```bash
   export AUTH_TOKEN=secret
   uvicorn release_server.main:app --reload
   ```

3. **Verify**:
   Visit `http://localhost:8000/docs` for API documentation.

### Docker Deployment

```bash
docker run -p 8000:8000 \
  -e AUTH_TOKEN=my-secret-token \
  -e MAX_PACKAGES=20 \
  -v $(pwd)/data:/data \
  ghcr.io/zlink-cloudtech/speckit-rs:latest
```

### Helm Deployment

Install directly from the OCI registry:

```bash
# Install the latest version
helm install release-server oci://ghcr.io/zlink-cloudtech/charts/speckit-rs --version 0.1.0

# Or install from specific version
helm install release-server oci://ghcr.io/zlink-cloudtech/charts/speckit-rs --version <VERSION>
```

## Configuration

Configuration is handled via Environment Variables or a YAML config file.

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTH_TOKEN` | *Required* | Bearer token for upload operations. |
| `MAX_PACKAGES` | `10` | Number of recent packages to keep. |
| `STORAGE_PATH` | `/data` | Directory to store package files. |
| `PORT` | `8000` | Listening port. |
| `CONFIG_PATH` | `config.yaml` | Path to YAML config file (optional). |

## API Endpoints

- `GET /latest`: Get metadata for the latest release (GitHub format).
- `GET /packages`: List all packages (supports `Accept: text/html`).
- `GET /assets/{filename}`: Download a specific package.
- `POST /upload`: Upload a new package (Requires `Authorization: Bearer <token>`).

## Spec Kit Integration

To use with `specify` CLI:

```bash
specify init --template-url http://your-release-server/latest
```

## Management Scripts

### Upload Script

A helper script is provided in [scripts/upload.sh](scripts/upload.sh) to simplify uploading packages to the server.

```bash
# Usage: ./release-server/scripts/upload.sh [options] <file_path>

./release-server/scripts/upload.sh -t "my-secret-token" dist/my-package.tar.gz
```

### Delete Script

A helper script is provided in [scripts/delete.sh](scripts/delete.sh) to manually delete specific packages.

```bash
# Usage: ./release-server/scripts/delete.sh [options] <filename>

./release-server/scripts/delete.sh -t "my-secret-token" my-package.tar.gz
```

**Options for both scripts:**

- `-u, --url <url>`: Server URL (default: `http://localhost:8000` or env `RELEASE_SERVER_URL`)
- `-t, --token <token>`: Auth Token (default: env `RELEASE_SERVER_TOKEN`)
- `-f, --force`: Overwrite existing file if it exists (Upload script only).

## Advanced: CI/CD & Local Workflow Testing

### GitHub Actions

The release server includes automated CI/CD workflows:

- `.github/workflows/release-server-ci.yml`: Runs tests and linters on push/PR.
- `.github/workflows/release-server-publish.yaml`: Builds and publishes Docker images/packages on tags.

### Testing Workflows Locally

To avoid "frequent commits" when debugging GitHub Actions, you can use **[act](https://github.com/nektos/act)**:

1. **Install act**: Follow instructions on the [act repository](https://github.com/nektos/act).

2. **Run Publish**:

   ```bash
   # Run from project root
   # Usage: ./.github/workflows/scripts/test-release-server.sh [options] [version]

   # Test complete workflow (Push event) - Default
   ./.github/workflows/scripts/test-release-server.sh

   # Test validation only (Pull Request event)
   ./.github/workflows/scripts/test-release-server.sh -e pull_request
   ```

   > **.secrets file content** (Required):
   >
   > - GITHUB_TOKEN=your_github_token_here

3. **Delete Artifacts**:

   After testing, you may want to clean up the created release artifacts on GitHub:

   1. Go to your repository's **Releases** page.
   2. Find the release named `v0.0.90-test` (or the version you used).
   3. Click on the release and then click **Delete** to remove it.
   4. Go to Packages tab, find the package named `release-server`, and delete the version you created.

### Manual Trigger

You can also test the publish workflow on GitHub without creating a tag by using the **Actions tab** and selecting **"Run workflow"** for the "Release Server Publish" action (uses `workflow_dispatch`).
