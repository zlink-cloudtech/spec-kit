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

## Testing

```bash
npm test
```
