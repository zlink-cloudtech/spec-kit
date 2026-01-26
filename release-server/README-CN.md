<div align="center">
  <h1>Release Server</h1>
  <p>用于托管和分发 Spec Kit 模板的轻量级 HTTP 服务器</p>
  
  [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/fastapi-0.109+-green.svg)](https://fastapi.tiangolo.com/)
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  
  [功能特性](#功能特性) • [快速开始](#快速开始) • [配置](#配置) • [API](#api-端点)
</div>

---

## 概述

Release Server 是一个生产就绪的 FastAPI 服务，为 Spec Kit 发布包提供安全、可扩展的托管。它与 `specify init` 工作流无缝集成，并支持通过 Docker 和 Kubernetes 进行容器化部署。

## 功能特性

- 📦 **包托管** - 通过 HTTP 上传和下载发布包，具有自动索引功能
- 🔐 **Token 认证** - 使用 Bearer Token 验证确保上传安全
- 🔑 **校验和验证** - 自动 SHA256 计算和验证以确保数据完整性
- 🔄 **GitHub 兼容性** - `/latest` 端点镜像 GitHub Release API 以实现直接集成
- 🧹 **自动保留** - 可配置的保留策略以管理包磁盘使用情况
- 🌐 **Web 界面** - 通过 `/packages` 的简单 HTML 列表浏览可用包
- 🐳 **容器化** - 预构建的 Docker 镜像和 Helm charts 随时可部署

## 快速开始

<details open>
<summary><h3>本地开发</h3></summary>

### 前置条件

- Python 3.12 或更高版本
- `pip` 或 `uv` 包管理器

### 安装和设置

1. 安装依赖项：

   ```bash
   cd release-server
   pip install -e .[dev]
   ```

   或使用 `uv`：

   ```bash
   uv sync --all-extras
   ```

2. 启动开发服务器：

   ```bash
   export AUTH_TOKEN=dev-secret-key
   uvicorn release_server.main:app --reload
   ```

3. 验证安装：
   - API 文档：<http://localhost:8000/docs>
   - 包列表：<http://localhost:8000/packages>
   - 健康检查：<http://localhost:8000/health>

</details>

<details>
<summary><h3>Docker 部署</h3></summary>

### 使用 Docker 运行

```bash
docker run -p 8000:8000 \
  -e AUTH_TOKEN=your-secure-token \
  -e MAX_PACKAGES=20 \
  -v release-data:/data \
  ghcr.io/zlink-cloudtech/speckit-rs:latest
```

### 使用 Docker Compose

```yaml
version: '3.8'
services:
  release-server:
    image: ghcr.io/zlink-cloudtech/speckit-rs:latest
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

### 使用 Helm 安装

```bash
helm install release-server oci://ghcr.io/zlink-cloudtech/charts/speckit-rs \
  --version 0.1.0 \
  --set authToken=your-secure-token
```

### 升级现有安装

```bash
helm upgrade release-server oci://ghcr.io/zlink-cloudtech/charts/speckit-rs \
  --version 0.1.0
```

有关高级 Helm 配置，请参见 [chart/README.md](chart/README.md)。

</details>

## 配置

可以通过**环境变量**或 **YAML 配置文件**设置配置。

### 环境变量

| 变量 | 默认值 | 必需 | 描述 |
|----------|---------|----------|-------------|
| `AUTH_TOKEN` | — | 是 | 用于上传授权的 Bearer Token |
| `MAX_PACKAGES` | `10` | 否 | 要保留的最近包数 |
| `STORAGE_PATH` | `/data` | 否 | 存储包文件的目录 |
| `PORT` | `8000` | 否 | 服务器监听端口 |
| `CONFIG_PATH` | `config.yaml` | 否 | 可选 YAML 配置文件的路径 |

### YAML 配置文件

示例 `config.yaml`：

```yaml
auth_token: your-secure-token
max_packages: 20
storage_path: /data
port: 8000
```

> [!TIP]
> 环境变量优先于 YAML 配置。

## API 端点

### 核心操作

| 方法 | 端点 | 描述 | 认证 |
|--------|----------|-------------|------|
| `GET` | `/health` | 健康检查端点 | 否 |
| `GET` | `/latest` | 最新发布元数据（GitHub API 格式） | 否 |
| `GET` | `/packages` | 列出所有包（HTML 或 JSON） | 否 |
| `GET` | `/assets/{filename}` | 下载特定包 | 否 |
| `POST` | `/upload` | 上传带元数据的新包 | 是 |
| `DELETE` | `/packages/{filename}` | 删除特定包 | 是 |

### 认证

上传和删除操作需要 `Authorization` header：

```bash
Authorization: Bearer YOUR_AUTH_TOKEN
```

### 请求示例

**列出包（JSON）**：

```bash
curl http://localhost:8000/packages \
  -H "Accept: application/json"
```

**下载包**：

```bash
curl -O http://localhost:8000/assets/my-package.tar.gz
```

**上传包**：

```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -F "file=@dist/my-package.tar.gz"
```

**删除包**：

```bash
curl -X DELETE http://localhost:8000/packages/my-package.tar.gz \
  -H "Authorization: Bearer $AUTH_TOKEN"
```

运行服务器时，访问 `/docs` 可获得交互式 API 文档。

## Spec Kit 集成

使用 Release Server 作为包源与 `specify` CLI：

```bash
specify init --template-url http://your-release-server/latest
```

这将无缝地将 Release Server 集成到 Spec Kit 初始化工作流中。

## 包管理

### 上传包

使用提供的上传辅助脚本：

```bash
./scripts/upload.sh -t "your-auth-token" dist/my-package.tar.gz
```

**选项：**

- `-u, --url <url>` — 服务器 URL（默认：`http://localhost:8000` 或 `$RELEASE_SERVER_URL`）
- `-t, --token <token>` — 认证 Token（默认：`$RELEASE_SERVER_TOKEN`）
- `-f, --force` — 覆盖现有包

### 删除包

```bash
./scripts/delete.sh -t "your-auth-token" my-package.tar.gz
```

**选项：**

- `-u, --url <url>` — 服务器 URL
- `-t, --token <token>` — 认证 Token

> [!NOTE]
> 两个脚本都支持环境变量 `RELEASE_SERVER_URL` 和 `RELEASE_SERVER_TOKEN` 作为默认值。

## CI/CD 和测试

### GitHub Actions 工作流

Release Server 包含自动化的 CI/CD 管道：

- **测试和检查**：`.github/workflows/release-server-ci.yml` — 在每次推送和拉取请求时运行
- **构建和发布**：`.github/workflows/release-server-publish.yaml` — 在版本标签上构建 Docker 镜像并发布

### 使用 Act 进行本地工作流测试

在没有创建提交的情况下本地测试 GitHub Actions：

1. **安装 [act](https://github.com/nektos/act)**，按照其文档操作

2. **创建 `.secrets` 文件**：

   ```ini
   GITHUB_TOKEN=your_github_token
   ```

3. **本地运行工作流**：

   ```bash
   # 测试完整工作流（推送事件）
   ./.github/workflows/scripts/test-release-server.sh

   # 仅测试验证（拉取请求事件）
   ./.github/workflows/scripts/test-release-server.sh -e pull_request
   ```

### 运行测试

```bash
# 运行测试套件
cd release-server
pytest

# 带覆盖率报告
pytest --cov=release_server
```

> [!WARNING]
> 使用 `act` 测试后，通过访问 GitHub 上的**发布版本**和**包**选项卡清理测试工件。

## 故障排除

### 常见问题

**端口已被使用**：

```bash
# 使用不同的端口
PORT=8001 uvicorn release_server.main:app
```

**认证失败**：

- 验证 `AUTH_TOKEN` 环境变量是否已设置
- 检查 Authorization header 格式：`Authorization: Bearer <token>`

**存储问题**：

- 确保 `STORAGE_PATH` 目录存在且可写
- 检查可用磁盘空间（遵守 `MAX_PACKAGES` 保留策略）

> [!TIP]
> 有关更多详情，请查看 [openapi.yaml](openapi.yaml) 规范或访问 `/docs` 端点。

## 资源

- 📖 [Spec Kit 文档](../docs/README.md)
- 🐋 [Docker Hub](https://ghcr.io/zlink-cloudtech/speckit-rs)
- 📦 [Helm Charts](chart/README.md)
- 🛠️ [Spec Kit 仓库](https://github.com/zlink-cloudtech/spec-kit)
- 📝 [OpenAPI 规范](openapi.yaml)

## 许可证

此项目根据 MIT 许可证获得许可 - 详见 [LICENSE](../LICENSE) 文件。

## 支持

- 🐛 [报告问题](https://github.com/zlink-cloudtech/spec-kit/issues)
- 💬 [讨论](https://github.com/zlink-cloudtech/spec-kit/discussions)
- 📧 维护者：<maintainers@zlinkcloudtech.com>
