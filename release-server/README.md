<div align="center">
  <h1>Release Server</h1>
  <p>Lightweight HTTP server for hosting and distributing Spec Kit templates</p>
  
  [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/fastapi-0.109+-green.svg)](https://fastapi.tiangolo.com/)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  
  [Features](#features) • [Quick Start](#quick-start) • [Configuration](#configuration) • [API](#api-endpoints)
</div>

---

## Overview

Release Server is a production-ready FastAPI service that provides secure, scalable hosting for Spec Kit release packages. It seamlessly integrates with the `specify init` workflow and supports containerized deployments via Docker and Kubernetes.

## Features

- 📦 **Package Hosting** - Upload and download release packages via HTTP with automatic indexing
- 🔐 **Token Authentication** - Secure uploads with Bearer token validation
- 🔑 **Checksum Verification** - Automatic SHA256 calculation and validation for data integrity
- 🔄 **GitHub Compatibility** - `/latest` endpoint mirrors GitHub Release API for drop-in integration
- 🧹 **Auto Retention** - Configurable retention policy to manage package disk usage
- 🌐 **Web Interface** - Browse available packages via simple HTML listing at `/packages`
- 🐳 **Containerized** - Pre-built Docker images and Helm charts ready for deployment

## Quick Start

<details open>
<summary><h3>Local Development</h3></summary>

### Prerequisites

- Python 3.12 or higher
- `pip` or `uv` package manager

### Installation & Setup

1. Install dependencies:

   ```bash
   cd release-server
   pip install -e .[dev]
   ```

   Or using `uv`:

   ```bash
   uv sync --all-extras
   ```

2. Start the development server:

   ```bash
   export AUTH_TOKEN=dev-secret-key
   uvicorn release_server.main:app --reload
   ```

3. Verify the installation:
   - API docs: <http://localhost:8000/docs>
   - Package listing: <http://localhost:8000/packages>
   - Health check: <http://localhost:8000/health>

</details>

<details>
<summary><h3>Docker Deployment</h3></summary>

### Run with Docker

```bash
docker run -p 8000:8000 \
  -e AUTH_TOKEN=your-secure-token \
  -e MAX_PACKAGES=20 \
  -v release-data:/data \
  ghcr.io/zlink-cloudtech/charts/speckit-rs:latest
```

### Using Docker Compose

```yaml
version: '3.8'
services:
  release-server:
    image: ghcr.io/zlink-cloudtech/charts/speckit-rs:latest
    ports:
      - "8000:8000"
    environment:
      AUTH_TOKEN: your-secure-token
      MAX_PACKAGES: 20
      STORAGE_PATH: /data
    volumes:
      - release-data:/data
      
volumes:
  release-data:
```

</details>

<details>
<summary><h3>Kubernetes / Helm</h3></summary>

### Install with Helm

```bash
helm install release-server oci://ghcr.io/zlink-cloudtech/charts/speckit-rs \
  --version 0.1.0 \
  --set authToken=your-secure-token
```

### Upgrade Existing Installation

```bash
helm upgrade release-server oci://ghcr.io/zlink-cloudtech/charts/speckit-rs \
  --version 0.1.0
```

For advanced Helm configuration, see [chart/README.md](chart/README.md).

</details>

## Configuration

Configuration can be set via **environment variables** or a **YAML configuration file**.

### Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `AUTH_TOKEN` | — | Yes | Bearer token for upload authorization |
| `MAX_PACKAGES` | `10` | No | Number of recent packages to retain |
| `STORAGE_PATH` | `/data` | No | Directory for storing package files |
| `PORT` | `8000` | No | Server listening port |
| `CONFIG_PATH` | `config.yaml` | No | Path to optional YAML config file |

### YAML Configuration File

Example `config.yaml`:

```yaml
auth_token: your-secure-token
max_packages: 20
storage_path: /data
port: 8000
```

> [!TIP]
> Environment variables take precedence over YAML configuration.

## API Endpoints

### Core Operations

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/health` | Health check endpoint | No |
| `GET` | `/latest` | Latest release metadata (GitHub API format) | No |
| `GET` | `/packages` | List all packages (HTML or JSON) | No |
| `GET` | `/assets/{filename}` | Download specific package | No |
| `POST` | `/upload` | Upload new package with metadata | Yes |
| `DELETE` | `/packages/{filename}` | Delete specific package | Yes |

### Authentication

Upload and delete operations require the `Authorization` header:

```bash
Authorization: Bearer YOUR_AUTH_TOKEN
```

### Example Requests

**List packages (JSON)**:

```bash
curl http://localhost:8000/packages \
  -H "Accept: application/json"
```

**Download package**:

```bash
curl -O http://localhost:8000/assets/my-package.tar.gz
```

**Upload package**:

```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -F "file=@dist/my-package.tar.gz"
```

**Delete package**:

```bash
curl -X DELETE http://localhost:8000/packages/my-package.tar.gz \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

For interactive API documentation, visit `/docs` when running the server.

## Spec Kit Integration

Use Release Server as a package source with the `specify` CLI:

```bash
specify init --template-url http://your-release-server/latest
```

This seamlessly integrates Release Server into the Spec Kit initialization workflow.

## Package Management

### Upload Packages

Use the provided upload helper script:

```bash
./scripts/upload.sh -t "your-auth-token" dist/my-package.tar.gz
```

**Options:**

- `-u, --url <url>` — Server URL (default: `http://localhost:8000` or `$RELEASE_SERVER_URL`)
- `-t, --token <token>` — Auth token (default: `$RELEASE_SERVER_TOKEN`)
- `-f, --force` — Overwrite existing package

### Delete Packages

```bash
./scripts/delete.sh -t "your-auth-token" my-package.tar.gz
```

**Options:**

- `-u, --url <url>` — Server URL
- `-t, --token <token>` — Auth token

> [!NOTE]
> Both scripts support environment variables `RELEASE_SERVER_URL` and `RELEASE_SERVER_TOKEN` as defaults.

## CI/CD & Testing

### GitHub Actions Workflows

Release Server includes automated CI/CD pipelines:

- **Test & Lint**: `.github/workflows/release-server-ci.yml` — Runs on every push and pull request
- **Build & Publish**: `.github/workflows/release-server-publish.yaml` — Builds Docker images and publishes on version tags

### Local Workflow Testing with Act

Test GitHub Actions locally without creating commits:

1. **Install [act](https://github.com/nektos/act)** following their documentation

2. **Create `.secrets` file**:

   ```ini
   GITHUB_TOKEN=your_github_token
   ```

3. **Run workflows locally**:

   ```bash
   # Test complete workflow (push event)
   ./.github/workflows/scripts/test-release-server.sh

   # Test validation only (pull request event)
   ./.github/workflows/scripts/test-release-server.sh -e pull_request
   ```

### Running Tests

```bash
# Run test suite
cd release-server
pytest

# With coverage report
pytest --cov=release_server
```

> [!WARNING]
> After testing with `act`, clean up test artifacts on GitHub by visiting **Releases** and **Packages** tabs.

## Troubleshooting

### Common Issues

**Port already in use**:

```bash
# Use a different port
PORT=8001 uvicorn release_server.main:app
```

**Authentication failures**:

- Verify `AUTH_TOKEN` environment variable is set
- Check Authorization header format: `Authorization: Bearer <token>`

**Storage issues**:

- Ensure `STORAGE_PATH` directory exists and is writable
- Check available disk space (respects `MAX_PACKAGES` retention policy)

> [!TIP]
> For more details, check the [openapi.yaml](openapi.yaml) specification or visit `/docs` endpoint.

## Resources

- 📖 [Spec Kit Documentation](../docs/README.md)
- 🐋 [Docker Hub](https://ghcr.io/zlink-cloudtech/charts/speckit-rs)
- 📦 [Helm Charts](chart/README.md)
- 🛠️ [Spec Kit Repository](https://github.com/zlink-cloudtech/spec-kit)
- 📝 [OpenAPI Specification](openapi.yaml)

## License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) file for details.

## Support

- 🐛 [Report Issues](https://github.com/zlink-cloudtech/spec-kit/issues)
- 💬 [Discussions](https://github.com/zlink-cloudtech/spec-kit/discussions)
- 📧 Maintainers: <maintainers@zlinkcloudtech.com>
