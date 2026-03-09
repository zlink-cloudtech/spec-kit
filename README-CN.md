<div align="center">
    <img src="./media/logo_large.webp" alt="Spec Kit Logo" width="200" height="200"/>
    <h1>🌱 Spec Kit</h1>
    <h3><em>更快地构建高质量软件。</em></h3>
</div>

<p align="center">
    <strong>一个开源工具包，让您专注于产品场景和可预测的结果，而不是从头开始编写每一行代码。</strong>
</p>

<p align="center">
    <a href="https://github.com/zlink-cloudtech/spec-kit/actions/workflows/release.yml"><img src="https://github.com/zlink-cloudtech/spec-kit/actions/workflows/release.yml/badge.svg" alt="Release"/></a>
    <a href="https://github.com/zlink-cloudtech/spec-kit/stargazers"><img src="https://img.shields.io/github/stars/zlink-cloudtech/spec-kit?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/zlink-cloudtech/spec-kit/blob/main/LICENSE"><img src="https://img.shields.io/github/license/zlink-cloudtech/spec-kit" alt="License"/></a>
    <a href="https://github.github.io/spec-kit/"><img src="https://img.shields.io/badge/docs-GitHub_Pages-blue" alt="Documentation"/></a>
</p>

---

## 目录

- [🤔 什么是 Spec-Driven Development？](#-什么是-spec-driven-development)
- [⚡ 开始使用](#-开始使用)
- [📽️ 视频概述](#️-视频概述)
- [🤖 支持的 AI 代理](#-支持的-ai-代理)
- [🔧 Specify CLI 参考](#-specify-cli-参考)
- [📚 核心理念](#-核心理念)
- [🌟 开发阶段](#-开发阶段)
- [🎯 实验目标](#-实验目标)
- [🔧 先决条件](#-先决条件)
- [📖 了解更多](#-了解更多)
- [📋 详细流程](#-详细流程)
- [🔍 故障排除](#-故障排除)
- [👥 维护者](#-维护者)
- [💬 支持](#-支持)
- [🙏 致谢](#-致谢)
- [📄 许可证](#-许可证)

## 🤔 什么是 Spec-Driven Development？

Spec-Driven Development **颠覆了** 传统的软件开发方式。几十年来，代码一直是王者——规范只是我们构建和丢弃的脚手架，一旦开始“真正的工作”编码就开始了。Spec-Driven Development 改变了这一点：**规范变得可执行**，直接生成工作实现，而不是仅仅指导它们。

## ⚡ 开始使用

### 1. 安装 Specify CLI

选择您偏好的安装方法：

#### 选项 1：持久安装（推荐）

安装一次，随处使用：

```bash
uv tool install specify-cli --from git+https://github.com/zlink-cloudtech/spec-kit.git
```

然后直接使用工具：

```bash
# 创建新项目
specify init <PROJECT_NAME>

# 或在现有项目中初始化
specify init . --ai claude
# 或
specify init --here --ai claude

# 检查已安装的工具
specify check
```

要升级 Specify，请参阅[升级指南](./docs/upgrade.md)以获取详细说明。快速升级：

```bash
uv tool install specify-cli --force --from git+https://github.com/zlink-cloudtech/spec-kit.git
```

#### 选项 2：一次性使用

无需安装即可直接运行：

```bash
uvx --from git+https://github.com/zlink-cloudtech/spec-kit.git specify init <PROJECT_NAME>
```

**持久安装的好处：**

- 工具保持安装并在 PATH 中可用
- 无需创建 shell 别名
- 使用 `uv tool list`、`uv tool upgrade`、`uv tool uninstall` 更好地管理工具
- 更清洁的 shell 配置

### 2. 建立项目原则

在项目目录中启动您的 AI 助手。助手中有 `/speckit.*` 命令可用。

使用 **`/speckit.constitution`** 命令创建项目的治理原则和发展指南，这些将指导所有后续开发。

```bash
/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

### 3. 创建规范

使用 **`/speckit.specify`** 命令描述您想要构建的内容。专注于 **什么** 和 **为什么**，而不是技术栈。

```bash
/speckit.specify Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping on the main page. Albums are never in other nested albums. Within each album, photos are previewed in a tile-like interface.
```

### 4. 创建技术实现计划

使用 **`/speckit.plan`** 命令提供您的技术栈和架构选择。

```bash
/speckit.plan The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible. Images are not uploaded anywhere and metadata is stored in a local SQLite database.
```

### 5. 拆分为任务

使用 **`/speckit.tasks`** 从您的实现计划创建可操作的任务列表。

```bash
/speckit.tasks
```

### 6. 执行实现

使用 **`/speckit.implement`** 执行所有任务并根据计划构建您的功能。

```bash
/speckit.implement
```

### 7. 收敛文档

使用 **`/speckit.converge`** 通过更新文档、ADR 和系统地图来完成功能。

```bash
/speckit.converge
```

有关详细的分步说明，请参阅我们的[综合指南](./spec-driven.md)。

## 📽️ 视频概述

想要观看 Spec Kit 的实际操作？观看我们的[视频概述](https://www.youtube.com/watch?v=a9eR1xsfvHg&pp=0gcJCckJAYcqIYzv)！

[![Spec Kit video header](/media/spec-kit-video-header.jpg)](https://www.youtube.com/watch?v=a9eR1xsfvHg&pp=0gcJCckJAYcqIYzv)

## 🤖 支持的 AI 代理

| 代理                                                                                | 支持 | 备注                                                                                                                                     |
| ------------------------------------------------------------------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| [Qoder CLI](https://qoder.com/cli)                                                   | ✅      |                                                                                                                                           |
| [Amazon Q Developer CLI](https://aws.amazon.com/developer/learning/q-developer-cli/) | ⚠️      | Amazon Q Developer CLI [不支持](https://github.com/aws/amazon-q-developer-cli/issues/3064) 斜杠命令的自定义参数。 |
| [Amp](https://ampcode.com/)                                                          | ✅      |                                                                                                                                           |
| [Auggie CLI](https://docs.augmentcode.com/cli/overview)                              | ✅      |                                                                                                                                           |
| [Claude Code](https://www.anthropic.com/claude-code)                                 | ✅      |                                                                                                                                           |
| [CodeBuddy CLI](https://www.codebuddy.ai/cli)                                        | ✅      |                                                                                                                                           |
| [Codex CLI](https://github.com/openai/codex)                                         | ✅      |                                                                                                                                           |
| [Cursor](https://cursor.sh/)                                                         | ✅      |                                                                                                                                           |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli)                            | ✅      |                                                                                                                                           |
| [GitHub Copilot](https://code.visualstudio.com/)                                     | ✅      |                                                                                                                                           |
| [IBM Bob](https://www.ibm.com/products/bob)                                          | ✅      | 支持斜杠命令的 IDE 基础代理                                                                                                |
| [Jules](https://jules.google.com/)                                                   | ✅      |                                                                                                                                           |
| [Kilo Code](https://github.com/Kilo-Org/kilocode)                                    | ✅      |                                                                                                                                           |
| [opencode](https://opencode.ai/)                                                     | ✅      |                                                                                                                                           |
| [Qwen Code](https://github.com/QwenLM/qwen-code)                                     | ✅      |                                                                                                                                           |
| [Roo Code](https://roocode.com/)                                                     | ✅      |                                                                                                                                           |
| [SHAI (OVHcloud)](https://github.com/ovh/shai)                                       | ✅      |                                                                                                                                           |
| [Windsurf](https://windsurf.com/)                                                    | ✅      |                                                                                                                                           |

## 🔧 Specify CLI 参考

`specify` 命令支持以下选项：

### 命令

| 命令 | 描述                                                                                                                                             |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `init`  | 从最新模板初始化新的 Specify 项目                                                                                               |
| `check` | 检查已安装的工具（`git`、`claude`、`gemini`、`code`/`code-insiders`、`cursor-agent`、`windsurf`、`qwen`、`opencode`、`codex`、`shai`、`qoder`） |

### `specify init` 参数和选项

| 参数/选项        | 类型     | 描述                                                                                                                                                                                  |
| ---------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<project-name>`       | 参数 | 新项目目录的名称（如果使用 `--here`，则可选，或使用 `.` 表示当前目录）                                                                                           |
| `--ai`                 | 选项   | 要使用的 AI 助手：`claude`、`gemini`、`copilot`、`cursor-agent`、`qwen`、`opencode`、`codex`、`windsurf`、`kilocode`、`auggie`、`roo`、`codebuddy`、`amp`、`shai`、`q`、`bob` 或 `qoder` |
| `--script`             | 选项   | 要使用的脚本变体：`sh` (bash/zsh) 或 `ps` (PowerShell)                                                                                                                                  |
| `--ignore-agent-tools` | 标志     | 跳过对 AI 代理工具（如 Claude Code）的检查                                                                                                                                              |
| `--no-git`             | 标志     | 跳过 git 仓库初始化                                                                                                                                                           |
| `--here`               | 标志     | 在当前目录中初始化项目，而不是创建新目录                                                                                                                    |
| `--force`              | 标志     | 在当前目录中初始化时强制合并/覆盖（跳过确认）                                                                                                             |
| `--skip-tls`           | 标志     | 跳过 SSL/TLS 验证（不推荐）                                                                                                                                                  |
| `--debug`              | 标志     | 启用详细调试输出以进行故障排除                                                                                                                                             |
| `--github-token`       | 选项   | 用于 API 请求的 GitHub 令牌（或设置 GH_TOKEN/GITHUB_TOKEN 环境变量）                                                                                                                    |
| `--template-url`       | 选项   | 要使用的自定义模板仓库的 URL（zip 文件），而不是默认模板                                                                                                                 |

### 示例

```bash
# 基本项目初始化
specify init my-project

# 使用特定 AI 助手初始化
specify init my-project --ai claude

# 使用 Cursor 支持初始化
specify init my-project --ai cursor-agent

# 使用 Qoder 支持初始化
specify init my-project --ai qoder

# 使用 Windsurf 支持初始化
specify init my-project --ai windsurf

# 使用 Amp 支持初始化
specify init my-project --ai amp

# 使用 SHAI 支持初始化
specify init my-project --ai shai

# 使用 IBM Bob 支持初始化
specify init my-project --ai bob

# 使用 PowerShell 脚本初始化（Windows/跨平台）
specify init my-project --ai copilot --script ps

# 在当前目录中初始化
specify init . --ai copilot
# 或使用 --here 标志
specify init --here --ai copilot

# 强制合并到当前（非空）目录而不确认
specify init . --force --ai copilot
# 或
specify init --here --force --ai copilot

# 跳过 git 初始化
specify init my-project --ai gemini --no-git

# 启用调试输出以进行故障排除
specify init my-project --ai claude --debug

# 使用 GitHub 令牌进行 API 请求（有助于企业环境）
specify init my-project --ai claude --github-token ghp_your_token_here

# 使用自定义模板初始化
specify init my-project --template-url https://example.com/template.zip
# 或本地文件 URL
specify init my-project --template-url file:///example.com/template.zip

# 检查系统要求
specify check
```

### 可用的斜杠命令

运行 `specify init` 后，您的 AI 编码代理将可以访问这些用于结构化开发的斜杠命令：

#### 核心命令

Spec-Driven Development 工作流程的基本命令：

| 命令                 | 描述                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| `/speckit.constitution` | 创建或更新项目治理原则和发展指南 |
| `/speckit.specify`      | 定义您想要构建的内容（需求和用户故事）            |
| `/speckit.plan`         | 使用您选择的技术栈创建技术实现计划        |
| `/speckit.tasks`        | 为实现生成可操作的任务列表                        |
| `/speckit.implement`    | 根据计划执行所有任务以构建功能             |
| `/speckit.converge`     | 完成功能——更新 ADR、系统地图并关闭文档差距 |

#### 可选命令

用于增强质量和验证的附加命令：

| 命令              | 描述                                                                                                                          |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `/speckit.clarify`   | 澄清未明确指定的领域（推荐在 `/speckit.plan` 之前运行；以前称为 `/quizme`）                                                |
| `/speckit.analyze`   | 跨工件一致性和覆盖分析（在 `/speckit.tasks` 之后、`/speckit.implement` 之前运行）                             |
| `/speckit.checklist` | 生成验证需求完整性、清晰度和一致性的自定义质量检查清单（如“英语的单元测试”） |

### 环境变量

| 变量          | 描述                                                                                                                                                                                                                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `SPECIFY_FEATURE` | 为非 Git 仓库覆盖功能检测。设置为包含类型前缀的完整分支名称（例如 `feat/001-photo-albums`），以在不使用 Git 分支时处理特定功能。<br/>\*\*必须在使用 `/speckit.plan` 或后续命令之前在您使用的代理上下文中设置。 |

## 📚 核心理念

Spec-Driven Development 是一个强调的结构化过程：

- **意图驱动开发** 规范在“如何”之前定义“什么”
- **丰富规范创建** 使用护栏和组织原则
- **多步细化** 而不是从提示中一次性生成代码
- **大量依赖** 高级 AI 模型能力进行规范解释

## 🌟 开发阶段

| 阶段                                    | 重点                    | 关键活动                                                                                                                                                     |
| ---------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **0 到 1 开发** ("Greenfield")    | 从头生成    | <ul><li>从高层需求开始</li><li>生成规范</li><li>规划实现步骤</li><li>构建生产就绪应用程序</li></ul> |
| **创意探索**                 | 并行实现 | <ul><li>探索多样化解决方案</li><li>支持多种技术栈和架构</li><li>实验 UX 模式</li></ul>                         |
| **迭代增强** ("Brownfield") | Brownfield 现代化 | <ul><li>迭代添加功能</li><li>现代化遗留系统</li><li>适应流程</li></ul>                                                                |

## 🎯 实验目标

我们的研究和实验重点：

### 技术独立性

- 使用多样化技术栈创建应用程序
- 验证 Spec-Driven Development 是过程而不是特定技术、编程语言或框架的假设

### 企业约束

- 演示关键任务应用程序开发
- 纳入组织约束（云提供商、技术栈、工程实践）
- 支持企业设计系统和合规要求

### 以用户为中心开发

- 为不同用户群体和偏好构建应用程序
- 支持各种开发方法（从凭感觉编码到 AI 原生开发）

### 创意和迭代过程

- 验证并行实现探索的概念
- 提供强大的迭代功能开发工作流程
- 将流程扩展到处理升级和现代化任务

## 🔧 先决条件

- **Linux/macOS/Windows**
- [支持的](#-支持的-ai-代理) AI 编码代理。
- [uv](https://docs.astral.sh/uv/) 用于包管理
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

如果您遇到代理问题，请打开一个 issue，以便我们完善集成。

## 📖 了解更多

- **[完整的 Spec-Driven Development 方法论](./spec-driven.md)** - 深入了解完整过程
- **[详细演练](#-详细流程)** - 分步实现指南

---

## 📋 详细流程

<details>
<summary>点击展开详细的分步演练</summary>

您可以使用 Specify CLI 来引导您的项目，这将在您的环境中引入所需的工件。运行：

```bash
specify init <project_name>
```

或在当前目录中初始化：

```bash
specify init .
# 或使用 --here 标志
specify init --here
# 当目录已有文件时跳过确认
specify init . --force
# 或
specify init --here --force
```

![Specify CLI 在终端中引导新项目](./media/specify_cli.gif)

系统将提示您选择正在使用的 AI 代理。您也可以直接在终端中主动指定：

```bash
specify init <project_name> --ai claude
specify init <project_name> --ai gemini
specify init <project_name> --ai copilot

# 或在当前目录中：
specify init . --ai claude
specify init . --ai codex

# 或使用 --here 标志
specify init --here --ai claude
specify init --here --ai codex

# 强制合并到非空当前目录
specify init . --force --ai claude

# 或
specify init --here --force --ai claude
```

CLI 将检查您是否安装了 Claude Code、Gemini CLI、Cursor CLI、Qwen CLI、opencode、Codex CLI、Qoder CLI 或 Amazon Q Developer CLI。如果没有，或者您更喜欢在不检查正确工具的情况下获取模板，请使用 `--ignore-agent-tools`：

```bash
specify init <project_name> --ai claude --ignore-agent-tools
```

### **步骤 1：** 建立项目原则

转到项目文件夹并运行您的 AI 代理。在我们的示例中，我们使用 `claude`。

![引导 Claude Code 环境](./media/bootstrap-claude-code.gif)

如果您看到 `/speckit.constitution`、`/speckit.specify`、`/speckit.plan`、`/speckit.tasks`、`/speckit.implement` 和 `/speckit.converge` 命令可用，则表示配置正确。

第一步应该是使用 `/speckit.constitution` 命令建立项目的治理原则。这有助于确保在所有后续开发阶段中保持一致的决策：

```text
/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements. Include governance for how these principles should guide technical decisions and implementation choices.
```

此步骤创建或更新 `.specify/memory/constitution.md` 文件，其中包含项目的 foundational 指南，AI 代理将在规范、规划和实现阶段引用这些指南。

### **步骤 2：** 创建项目规范

建立项目原则后，您现在可以创建功能规范。使用 `/speckit.specify` 命令，然后提供您要开发的项目的具体需求。

> [!IMPORTANT]
> 尽可能明确您尝试构建的*什么*和*为什么*。**此时不要关注技术栈**。

示例提示：

```text
Develop Taskify, a team productivity platform. It should allow users to create projects, add team members,
assign tasks, comment and move tasks between boards in Kanban style. In this initial phase for this feature,
let's call it "Create Taskify," let's have multiple users but the users will be declared ahead of time, predefined.
I want five users in two different categories, one product manager and four engineers. Let's create three
different sample projects. Let's have the standard Kanban columns for the status of each task, such as "To Do,"
"In Progress," "In Review," and "Done." There will be no login for this application as this is just the very
first testing thing to ensure that our basic features are set up. For each task in the UI for a task card,
you should be able to change the current status of the task between the different columns in the Kanban work board.
You should be able to leave an unlimited number of comments for a particular card. You should be able to, from that task
card, assign one of the valid users. When you first launch Taskify, it's going to give you a list of the five users to pick
from. There will be no password required. When you click on a user, you go into the main view, which displays the list of
projects. When you click on a project, you open the Kanban board for that project. You're going to see the columns.
You'll be able to drag and drop cards back and forth between different columns. You will see any cards that are
assigned to you, the currently logged in user, in a different color from all the other ones, so you can quickly
see yours. You can edit any comments that you make, but you can't edit comments that other people made. You can
delete any comments that you make, but you can't delete comments anybody else made.
```

输入此提示后，您应该看到 Claude Code 开始规划和规范起草过程。Claude Code 还将触发一些内置脚本来设置仓库。

完成此步骤后，您应该有一个新分支创建（例如 `001-create-taskify`），以及 `specs/001-create-taskify` 目录中的新规范。

生成的规范应包含模板中定义的一组用户故事和功能需求。

此时，您的项目文件夹内容应类似于以下：

```text
└── .specify
    ├── memory
    │  └── constitution.md
    ├── scripts
    │  ├── check-prerequisites.sh
    │  ├── common.sh
    │  ├── create-new-feature.sh
    │  ├── setup-plan.sh
    │  └── update-claude-md.sh
    ├── specs
    │  └── 001-create-taskify
    │      └── spec.md
    └── templates
        ├── plan-template.md
        ├── spec-template.md
        └── tasks-template.md
```

### **步骤 3：** 功能规范澄清（规划前必需）

创建基准规范后，您可以澄清第一次尝试中未正确捕获的任何需求。

您应该在创建技术计划之前运行结构化澄清工作流程，以减少下游返工。

首选顺序：

1. 使用 `/speckit.clarify`（结构化）– 顺序、基于覆盖的提问，将答案记录在澄清部分。
2. 如果仍需要，可以选择跟随即兴自由形式细化。

如果您有意跳过澄清（例如，尖峰或探索性原型），请明确说明，以便代理不会因缺失澄清而阻塞。

示例自由形式细化提示（如果 `/speckit.clarify` 后仍需要）：

```text
For each sample project or project that you create there should be a variable number of tasks between 5 and 15
tasks for each one randomly distributed into different states of completion. Make sure that there's at least
one task in each stage of completion.
```

您还应该要求 Claude Code 验证**审查和验收检查清单**，检查符合要求的项目，并留下不符合的未选中。可以使用以下提示：

```text
Read the review and acceptance checklist, and check off each item in the checklist if the feature spec meets the criteria. Leave it empty if it does not.
```

重要的是，将与 Claude Code 的交互作为澄清和询问规范问题的机会 - **不要将其第一次尝试视为最终**。

### **步骤 4：** 生成计划

您现在可以具体说明技术栈和其他技术要求。您可以使用项目模板中内置的 `/speckit.plan` 命令，提示如下：

```text
We are going to generate this using .NET Aspire, using Postgres as the database. The frontend should use
Blazor server with drag-and-drop task boards, real-time updates. There should be a REST API created with a projects API,
tasks API, and a notifications API.
```

此步骤的输出将包括许多实现细节文档，您的目录树类似于：

```text
.
├── CLAUDE.md
├── memory
│  └── constitution.md
├── scripts
│  ├── check-prerequisites.sh
│  ├── common.sh
│  ├── create-new-feature.sh
│  ├── setup-plan.sh
│  └── update-claude-md.sh
├── specs
│  └── 001-create-taskify
│      ├── contracts
│      │  ├── api-spec.json
│      │  └── signalr-spec.md
│      ├── data-model.md
│      ├── plan.md
│      ├── quickstart.md
│      ├── research.md
│      └── spec.md
└── templates
    ├── CLAUDE-template.md
    ├── plan-template.md
    ├── spec-template.md
    └── tasks-template.md
```

检查 `research.md` 文档以确保根据您的说明使用了正确的技术栈。如果任何组件突出，您可以要求 Claude Code 细化它，甚至让它检查您要使用的平台/框架的本地安装版本（例如 .NET）。

此外，如果它是快速变化的东西（例如 .NET Aspire、JS 框架），您可能希望要求 Claude Code 研究所选技术栈的细节，提示如下：

```text
I want you to go through the implementation plan and implementation details, looking for areas that could
benefit from additional research as .NET Aspire is a rapidly changing library. For those areas that you identify that
require further research, I want you to update the research document with additional details about the specific
versions that we are going to be using in this Taskify application and spawn parallel research tasks to clarify
any details using research from the web.
```

在此过程中，您可能会发现 Claude Code 卡在研究错误的东西 - 您可以使用如下提示帮助引导它：

```text
I think we need to break this down into a series of steps. First, identify a list of tasks
that you would need to do during implementation that you're not sure of or would benefit
from further research. Write down a list of those tasks. And then for each one of these tasks,
I want you to spin up a separate research task so that the net results is we are researching
all of those very specific tasks in parallel. What I saw you doing was it looks like you were
researching .NET Aspire in general and I don't think that's gonna do much for us in this case.
That's way too untargeted research. The research needs to help you solve a specific targeted question.
```

> [!NOTE]
> Claude Code 可能过于热心并添加您未要求的组件。要求它澄清理由和变更来源。

### **步骤 5：** 让 Claude Code 验证计划

计划到位后，您应该让 Claude Code 检查以确保没有缺失部分。您可以使用如下提示：

```text
Now I want you to go and audit the implementation plan and the implementation detail files.
Read through it with an eye on determining whether or not there is a sequence of tasks that you need
to be doing that are obvious from reading this. Because I don't know if there's enough here. For example,
when I look at the core implementation, it would be useful to reference the appropriate places in the implementation
details where it can find the information as it walks through each step in the core implementation or in the refinement.
```

这有助于细化实现计划，并帮助您避免 Claude Code 在规划周期中错过的潜在盲点。一旦初始细化通过完成，要求 Claude Code 在实施前再次检查清单。

如果您安装了 [GitHub CLI](https://docs.github.com/en/github-cli/github-cli)，您还可以要求 Claude Code 从当前分支到 `main` 创建一个带有详细描述的拉取请求，以确保努力得到适当跟踪。

> [!NOTE]
> 在让代理实施之前，也值得提示 Claude Code 交叉检查细节，看是否有过度工程的部分（记住 - 它可能过于热心）。如果存在过度工程的组件或决策，您可以要求 Claude Code 解决它们。确保 Claude Code 遵循 [constitution](base/memory/constitution.md) 作为建立计划时必须遵守的基础。

### **步骤 6：** 使用 /speckit.tasks 生成任务分解

验证实现计划后，您现在可以将计划分解为可以正确顺序执行的特定、可操作任务。使用 `/speckit.tasks` 命令从您的实现计划自动生成详细任务分解：

```text
/speckit.tasks
```

此步骤在您的功能规范目录中创建一个 `tasks.md` 文件，其中包含：

- **按用户故事组织的任务分解** - 每个用户故事成为一个单独的实现阶段，具有自己的任务集
- **依赖管理** - 任务排序以尊重组件之间的依赖（例如，模型在服务之前，服务在端点之前）
- **并行执行标记** - 可以并行运行的任务标记为 `[P]` 以优化开发工作流程
- **文件路径规范** - 每个任务包括实现应发生的精确文件路径
- **测试驱动开发结构** - 如果请求测试，则包括测试任务并排序为在实现之前编写
- **检查点验证** - 每个用户故事阶段包括检查点以验证独立功能

生成的 tasks.md 为 `/speckit.implement` 命令提供清晰路线图，确保系统实现，保持代码质量，并允许用户故事的增量交付。

### **步骤 7：** 实施

准备就绪后，使用 `/speckit.implement` 命令执行您的实现计划：

```text
/speckit.implement
```

`/speckit.implement` 命令将：

- 验证所有先决条件到位（constitution、spec、plan 和 tasks）
- 从 `tasks.md` 解析任务分解
- 按正确顺序执行任务，尊重依赖和并行执行标记
- 遵循任务计划中定义的 TDD 方法
- 提供进度更新并适当处理错误

> [!IMPORTANT]
> AI 代理将执行本地 CLI 命令（如 `dotnet`、`npm` 等） - 确保您的机器上安装了所需工具。

实施完成后，测试应用程序并解决 CLI 日志中不可见的任何运行时错误（例如，浏览器控制台错误）。您可以将此类错误复制并粘贴回您的 AI 代理以解决。

### **步骤 8：** 收敛文档

验证实施后，使用 `/speckit.converge` 命令通过更新所有文档、ADR 和系统地图来完成功能：

```text
/speckit.converge
```

`/speckit.converge` 命令将：

- 在 `tasks.md` 中的 `<!-- CONVERGENCE_BOUNDARY -->` 下方找到所有第 N 阶段任务
- 在继续之前验证所有实施任务（第 1 至 N-1 阶段）已完成
- 执行文档收敛任务：更新 ADR、同步系统地图，并关闭计划文档状态矩阵中确定的每个差距
- 执行后将每个收敛任务标记为完成

> [!NOTE]
> 收敛是强制性的、不可跳过的阶段。`/speckit.implement` 在 `CONVERGENCE_BOUNDARY` 处强制硬停止——只有 `/speckit.converge` 可以执行第 N 阶段任务。

</details>

---

## 🔍 故障排除

### Linux 上的 Git Credential Manager

如果您在 Linux 上遇到 Git 身份验证问题，可以安装 Git Credential Manager：

```bash
#!/usr/bin/env bash
set -e
echo "Downloading Git Credential Manager v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "Installing Git Credential Manager..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "Configuring Git to use GCM..."
git config --global credential.helper manager
echo "Cleaning up..."
rm gcm-linux_amd64.2.6.1.deb
```

## 👥 维护者

- Den Delimarsky ([@localden](https://github.com/localden))
- John Lam ([@jflam](https://github.com/jflam))

## 💬 支持

有关支持，请打开 [GitHub issue](https://github.com/zlink-cloudtech/spec-kit/issues/new)。我们欢迎错误报告、功能请求以及有关使用 Spec-Driven Development 的问题。

## 🙏 致谢

此项目深受 [John Lam](https://github.com/jflam) 的工作和研究影响并基于此。

## 📄 许可证

此项目根据 MIT 开源许可证条款授权。请参阅 [LICENSE](./LICENSE) 文件以获取完整条款。
