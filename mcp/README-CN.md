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

## Helm Chart（Kubernetes 部署）

使用内置 Helm chart 将 MCP 服务器部署到 Kubernetes，支持两种部署模式：

- **镜像模式**（默认）：使用预构建的容器镜像部署
- **NPM 模式**：通过 init 容器在运行时安装 NPM 包

### 快速安装

```bash
# 从 GHCR（OCI 注册表）安装
helm install my-mcp oci://ghcr.io/zlink-cloudtech/speckit-mcp-server --version <version>

# 从本地源安装
helm install my-mcp ./chart
```

### NPM 模式

```bash
helm install my-mcp ./chart \
  --set mode=npm \
  --set npm.version=0.1.1
```

### 验证部署

```bash
kubectl get pods -l app.kubernetes.io/name=speckit-mcp-server
kubectl port-forward svc/my-mcp-speckit-mcp-server 8080:8080
```

完整的配置选项、网络配置（Ingress / Gateway API HTTPRoute）和故障排除，请参阅 [chart 文档](./chart/README.md)。

## 测试

```bash
npm test
```
