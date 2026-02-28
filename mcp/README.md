# Speckit MCP Server

An MCP server for Spec Kit, providing technical document translation prompts.

## Building the Project

```bash
npm run build
```

## Installation

```bash
npm install
```

## Usage

### Stdio Mode (Default)

```bash
npm run start:stdio
```

### HTTP/SSE Mode

```bash
npm run start:http
# or
node dist/index.js --port 3000
```

## Docker

Build the image:

```bash
./scripts/build-docker.sh
```

Run:

```bash
docker run -i speckit-mcp-server:latest
```

## Publishing & Remote Usage

### Publish to Private Registry

1. Configure `package.json` with your registry URL:

   ```json
   "publishConfig": {
     "registry": "http://npm.svc.home"
   }
   ```

2. Build and publish:

   ```bash
   npm run build
   npm publish
   # Or explicitly: npm publish --registry http://npm.svc.home
   ```

### Run from Registry

You can run the published server directly without cloning the repo:

```bash
# Run via Stdio (default)
npx -y --registry http://npm.svc.home speckit-mcp-server@latest

# Run via HTTP
npx -y --registry http://npm.svc.home speckit-mcp-server@latest --port 3000
```

### Client Configuration (e.g. Claude Desktop)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "speckit": {
      "command": "npx",
      "args": [
        "-y",
        "--registry",
        "http://npm.svc.home",
        "speckit-mcp-server@latest"
      ]
    }
  }
}
```

## Helm Chart (Kubernetes Deployment)

Deploy the MCP server to Kubernetes using the included Helm chart with two deployment modes:

- **Image mode** (default): Deploy from a pre-built container image
- **NPM mode**: Install the NPM package at runtime via an init container

### Quick Install

```bash
# From GHCR (OCI registry)
helm install my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server --version <version>

# From local source
helm install my-mcp ./chart
```

### NPM Mode

```bash
helm install my-mcp ./chart \
  --set mode=npm \
  --set npm.version=0.1.1
```

### Verify Deployment

```bash
kubectl get pods -l app.kubernetes.io/name=speckit-mcp-server
kubectl port-forward svc/my-mcp-speckit-mcp-server 8080:8080
```

For full configuration options, networking (Ingress / Gateway API HTTPRoute), and troubleshooting, see the [chart documentation](./chart/README.md).

## Testing

```bash
npm test
```
