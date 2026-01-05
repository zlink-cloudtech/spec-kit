# Speckit MCP 服务器

为 Spec Kit 提供技术文档翻译提示的 MCP 服务器。

## 构建项目

```bash
npm run build
```

## 安装

```bash
npm install
```

## 使用方法

### Stdio 模式（默认）

```bash
npm run start:stdio
```

### HTTP/SSE 模式

```bash
npm run start:http
# or
node dist/index.js --port 3000
```

## Docker

构建镜像：

```bash
./scripts/build-docker.sh
```

运行：

```bash
docker run -i speckit-mcp-server:latest
```

## 测试

```bash
npm test
```