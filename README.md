# AI Dev Team

> **AI 软件公司模拟系统** - 主 Agent 统筹，子 Agent 执行，人类最终验收

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green)](https://clawhub.ai)

AI 驱动的自主开发团队管理系统。模拟真实软件公司架构，让 AI 自主完成开发任务。

---

## 🎯 愿景

```
人类（甲方）
    ↓ 需求对齐 / 验收确认
主 Agent（CEO）
    ├─ 项目分析 → 生成规划
    ├─ 任务拆分 → 状态机管理
    ├─ 指派子 Agent（单任务单 Agent）
    ├─ 验收评估 → Git 提交
    └─ 异常上报 → 人类决策
        ↓
    子 Agent（员工）- 执行后销毁
        ├─ Developer（开发）
        ├─ Tester（测试）
        └─ Researcher（文档）
```

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🏢 **公司模拟** | 主 Agent 如 CEO，子 Agent 如员工，人类如甲方 |
| 🔄 **状态机驱动** | 13 状态完整任务生命周期管理 |
| 👤 **单任务单 Agent** | 资源节制，职责明确，避免冲突 |
| 📝 **Git 可追溯** | 所有 AI 提交带元数据，可查询可回滚 |
| 📊 **分层上报** | AI 自主决策，必要时上报人类 |
| 🛠️ **通用框架** | 不绑定特定技术栈，适配任何项目 |

---

## 🚀 快速开始

### 1. 初始化项目

```bash
# 在 Git 项目根目录执行
@ai-dev-team init
```

创建 `.ai-dev-team/` 目录结构和配置文件。

### 2. 分析项目

```bash
@ai-dev-team analyze
```

主 Agent 将：
- 扫描项目结构
- 识别技术栈
- 发现潜在优化点
- 生成《项目分析报告》

### 3. 生成规划

```bash
@ai-dev-team plan
```

将发现的任务转为开发规划，等待人类确认。

### 4. 开始开发

```bash
# 手动批准每个任务
@ai-dev-team start

# 或自动批准（谨慎使用）
@ai-dev-team start --auto-approve
```

### 5. 验收任务

```bash
# 批准任务
@ai-dev-team approve --task-id=t-123456

# 拒绝任务（返回重新分析）
@ai-dev-team approve --task-id=t-123456 --reject
```

### 6. 查看状态

```bash
@ai-dev-team status
```

---

## 📋 命令参考

| 命令 | 说明 | 参数 |
|------|------|------|
| `init` | 初始化项目 | `[项目路径]` |
| `analyze` | 分析项目 | - |
| `plan` | 生成规划 | - |
| `start` | 开始开发循环 | `--auto-approve` |
| `status` | 查看状态 | - |
| `approve` | 验收任务 | `--task-id=<id>`, `--reject` |

---

## 🗂️ 目录结构

```
project/
├── .ai-dev-team/
│   ├── config.json          # 配置
│   ├── state.json           # 状态机（TOON 格式）
│   ├── tasks/               # 任务卡片
│   │   └── t-xxx.json
│   ├── reports/             # 执行报告
│   │   ├── project-analysis-*.md
│   │   ├── dev-plan-*.md
│   │   └── execution-*.md
│   └── logs/                # Agent 日志
├── agents/                  # Agent 角色定义
│   ├── developer/SOUL.md
│   ├── tester/SOUL.md
│   └── researcher/SOUL.md
├── scripts/                 # 核心脚本
│   ├── main_agent.py        # 主 Agent
│   ├── state_manager.py     # 状态管理
│   ├── git_wrapper.py       # Git 封装
│   └── init_project.py      # 初始化
├── index.py                 # 入口
└── package.json             # Skill 配置
```

---

## 🔄 状态机

```
DISCOVERED → ANALYZING → PLANNING → PENDING_APPROVAL → ASSIGNED 
                                                              ↓
COMPLETED ← TESTING ← IN_PROGRESS ←←←←←←←←←←←←←←←←←←←←←←┘
   ↓
git commit

异常分支:
IN_PROGRESS → 重试超限 → ESCALATED → 人类决策
PENDING_APPROVAL → 拒绝 → CANCELLED
```

### 状态说明

| 状态 | 说明 |
|------|------|
| `DISCOVERED` | 新发现的任务 |
| `ANALYZING` | 正在分析需求 |
| `PLANNING` | 生成实现方案 |
| `PENDING_APPROVAL` | 等待人类批准 |
| `ASSIGNED` | 已指派子 Agent |
| `IN_PROGRESS` | 子 Agent 执行中 |
| `TESTING` | 主 Agent 验证中 |
| `PENDING_HUMAN_TEST` | 等待人类验收 |
| `COMPLETED` | 已完成并提交 |
| `ESCALATED` | 需要人类介入 |
| `CANCELLED` | 已取消 |

---

## ⚙️ 配置

`.ai-dev-team/config.json`：

```json
{
  "workflow": {
    "auto_approve": false,      // 自动批准任务（谨慎！）
    "require_human_test": true,  // 需要人类验收
    "max_concurrent_agents": 1,  // 最大并发 Agent 数
    "default_timeout": "2h",     // 默认超时
    "max_retries": 3             // 最大重试次数
  },
  "escalation": {
    "threshold": 3,              // 上报阈值
    "consecutive_failures": 3    // 连续失败阈值
  },
  "git": {
    "auto_commit": true,         // 自动提交
    "commit_prefix": "[AI]",     // 提交前缀
    "traceability": true         // 启用可追溯
  }
}
```

---

## 📊 Git 可追溯

所有 AI 提交包含元数据：

```
[AI-t-123456] feat: 添加用户认证

AI-Task: t-123456
AI-Agent: dev-001
AI-Time: 2026-03-28T21:00:00
AI-Report: .ai-dev-team/reports/execution-t-123456.md
```

### 查询 AI 提交

```bash
# 查看所有 AI 提交
git log --grep="[AI-"

# 查看特定任务提交
git log --grep="AI-Task: t-123456"

# 查看提交详情
git show <commit-hash>
```

---

## 🤖 Agent 角色

### Main Agent (CEO)
- 项目分析与规划
- 任务拆分与指派
- 验收决策
- 异常上报

### Developer Agent
- 读取任务卡片
- 实现功能
- 自测
- 生成执行报告

### Tester Agent
- 审查代码变更
- 运行测试
- 视觉验证
- 生成测试报告

### Researcher Agent
- 收集官方文档
- 技术调研
- 编写文档
- 知识整理

---

## 📁 报告模板

### 项目分析报告
- 技术栈识别
- 文件统计
- 潜在任务列表

### 执行报告
- 任务信息
- 完成的工作
- 修改的文件
- 测试结果
- 遇到的问题

### 上报报告
- 问题描述
- 已尝试方案
- 建议选项
- 需要人类决策的点

---

## 🔧 扩展

### 添加新 Agent 类型

在 `agents/` 目录创建新角色：

```
agents/
└── your-agent/
    └── SOUL.md
```

### 自定义报告模板

在 `assets/templates/` 添加模板。

### 集成外部工具

- **Context7** - 获取 API 文档
- **GitHub Actions** - CI/CD 集成
- **多模态模型** - UI 截图验证

---

## 📚 文档

- [详细架构](references/architecture.md)
- [状态机定义](references/state-machine.md)
- [任务协议](references/task-protocol.md)
- [Agent 类型](references/agent-types.md)
- [MVP 实现](references/mvp-implementation.md)
- [故障排查](references/troubleshooting.md)

---

## 🏷️ 版本

**v1.0.0** - 初始发布
- ✅ 主 Agent 核心逻辑
- ✅ 子 Agent 框架
- ✅ 状态机管理
- ✅ Git 可追溯
- ✅ 报告系统

---

## 📄 License

[GPL-3.0](LICENSE) - 自由软件，欢迎贡献！

---

## 🙏 致谢

- OpenClaw 团队提供 subagents 和 skill 系统
- 社区反馈和建议

---

*AI Dev Team - 让 AI 自主开发，人类专注决策* ⚡
