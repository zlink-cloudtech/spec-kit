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

## Testing

```bash
npm test
```
