# AI Dev Team - 自主开发团队 🤖

> **AI 软件公司模拟系统** - 主 Agent 统筹，子 Agent 执行，人类最终验收
> **v1.1.0** - 基于 OpenClaw 原生多 Agent 架构（sessions_spawn）

[![Version](https://img.shields.io/badge/version-1.1.0-blue)](https://github.com/openclaw/openclaw)
[![Python](https://img.shields.io/badge/python-3.8+-green)](https://python.org)
[![License](https://img.shields.io/badge/license-GPL--3.0-yellow)](LICENSE)

---

## 🚀 快速开始

### 1. 配置多 Agent（必需）

在 `~/.openclaw/gateway.config.json` 中添加配置：

```bash
# 详见 references/openclaw-multiagent-config.md
# 需要配置 4 个 Agent: main/developer/tester/researcher
```

### 2. 安装依赖（可选）

```bash
# Context7（用于文档收集）
clawhub install context7
```

### 3. 初始化项目

```bash
# 在 Git 项目根目录执行
@ai-dev-team init
```

### 3. 分析项目

```bash
@ai-dev-team analyze
```

### 4. 生成规划

```bash
@ai-dev-team plan
```

### 5. 开始开发

```bash
@ai-dev-team start              # 手动批准模式
@ai-dev-team start --auto-approve  # 自动批准模式
```

### 6. 验收任务

```bash
# 查看待验收任务
@ai-dev-team approve

# 批准任务
@ai-dev-team approve --task-id=t-123 --approved=true
```

---

## 📋 命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `init` | 初始化项目 | `@ai-dev-team init` |
| `analyze` | 分析项目 | `@ai-dev-team analyze` |
| `plan` | 生成规划 | `@ai-dev-team plan` |
| `start` | 开始开发循环 | `@ai-dev-team start --auto-approve` |
| `status` | 查看状态 | `@ai-dev-team status` |
| `approve` | 验收任务 | `@ai-dev-team approve --task-id=t-123` |
| `escalations` | 查看上报 | `@ai-dev-team escalations` |
| `research` | 文档调研 | `@ai-dev-team research --library=react --query=hooks` |

---

## 🏗️ 架构

```
人类（甲方）
    ↓ 需求对齐 / 验收确认 / 异常决策
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

## 🔄 工作流程

### 标准流程

```
1. 初始化 → 2. 分析 → 3. 规划 → 4. 开发循环
                                       ↓
5. 验收 ← 4c. 测试 ← 4b. 开发 ← 4a. 调研（可选）
```

### 状态机

```
DISCOVERED → ANALYZING → PLANNING → PENDING_APPROVAL → ASSIGNED
                                                              ↓
COMPLETED ← TESTING ← IN_PROGRESS ←←←←←←←←←←←←←←←←←←←←←←┘
       ↑                    ↓
       └──── ESCALATED ←───┘ (重试超限)
```

---

## 📁 目录结构

```
项目/
└── .ai-dev-team/
    ├── config.json       # 配置
    ├── state.json        # 状态机
    ├── tasks/            # 任务卡片
    ├── reports/          # 报告
    ├── docs/             # 文档缓存
    ├── logs/             # 日志
    └── README.md         # 项目说明
```

---

## 🤖 Agent 角色

### Main Agent (CEO)

- 项目分析、任务规划
- 子 Agent 指派
- 验收决策、异常上报

**实现:** `scripts/main_agent.py`

### Developer Agent (开发工程师)

- 读取任务和相关代码
- 实现功能/修复 Bug
- 运行自测
- 生成执行报告

**实现:** `scripts/developer_agent.py`

### Tester Agent (测试工程师)

- 审查代码变更（git diff）
- 运行测试套件
- 检查执行报告
- 检测敏感信息泄露

**实现:** `scripts/tester_agent.py`

### Researcher Agent (文档研究员)

- 使用 Context7 收集官方文档
- 缓存技术文档
- 生成调研报告

**实现:** `scripts/researcher_agent.py`

---

## ⚙️ 配置

`.ai-dev-team/config.json`:

```json
{
  "workflow": {
    "auto_approve": false,      // 是否自动批准
    "require_human_test": true, // 需要人类测试
    "max_retries": 3            // 最大重试次数
  },
  "git": {
    "auto_commit": true,        // 自动提交
    "traceability": true        // 可追溯元数据
  }
}
```

---

## 📊 Git 可追溯

所有 AI 提交包含元数据：

```
[AI-t-123] feat: 添加功能

AI-Task: t-123
AI-Agent: dev-001
AI-Time: 2026-03-28T21:00:00
AI-Report: .ai-dev-team/reports/execution-t-123.md
```

**查询:**

```bash
git log --grep="[AI-"
git log --grep="AI-Task: t-123"
```

---

## 📚 文档收集

### 使用 Context7

```bash
# 搜索文档
@ai-dev-team research --library=vercel/next.js --query="API routes"

# 自动收集（开发前）
# Researcher Agent 会自动判断是否需要文档
# 并调用 Context7 获取官方 API 文档
```

### 文档缓存

缓存位置：`.ai-dev-team/docs/`

格式：

```markdown
---
title: Next.js API 参考
source: vercel/next.js
cached_at: 2026-03-28T21:00:00
tags: api, reference, next.js
---

[文档内容]
```

---

## 🧪 测试验证

Tester Agent 自动执行：

1. **代码审查**
   - Git diff 检查
   - 敏感信息检测
   - 行数统计

2. **测试运行**
   - pytest（Python）
   - npm test（Node.js）
   - jest（JavaScript）

3. **报告检查**
   - 执行报告完整性
   - 必需元素验证

---

## 🚨 上报机制

**上报条件:**

- 重试次数 ≥ 3 次
- 连续失败 ≥ 3 次
- 系统性异常

**上报流程:**

```
任务失败 → 检查重试 → 未超限：重试
                      ↓
                  已超限：上报
                      ↓
                生成上报报告
                      ↓
                人类决策（A/B/C）
```

---

## 🛠️ 扩展开发

### 添加新 Agent

1. 在 `scripts/` 创建 Agent 类
2. 在 `agents/` 添加 SOUL.md
3. 在 `main_agent.py` 添加提示构建

### 自定义报告

在 `assets/templates/` 添加 Markdown 模板

### 集成新工具

参考 `researcher_agent.py` 的 Context7 集成

---

## 📖 详细文档

- [完整实现说明](references/implementation-complete.md)
- [架构设计](references/architecture.md)
- [状态机](references/state-machine.md)
- [任务协议](references/task-protocol.md)
- [Agent 类型](references/agent-types.md)
- [故障排查](references/troubleshooting.md)

---

## 🔧 故障排查

### 任务卡住

```bash
# 检查状态
@ai-dev-team status

# 查看活跃任务
python scripts/state_manager.py list AS
```

### 子 Agent 失败

```bash
# 查看执行报告
cat .ai-dev-team/reports/execution-<task-id>.md

# 查看测试报告
cat .ai-dev-team/reports/test-<task-id>.md
```

### Context7 无结果

```bash
# 检查 API key
cat skills/context7/.env

# 测试 Context7
cd skills/context7
npx tsx query.ts context "vercel/next.js" "API"
```

---

## 📝 示例

### 新项目初始化

```bash
# 1. 初始化
@ai-dev-team init

# 2. 分析
@ai-dev-team analyze
# 输出：识别到 Python 项目，发现 5 个潜在任务

# 3. 规划
@ai-dev-team plan
# 输出：5 个任务加入待批准队列

# 4. 开发
@ai-dev-team start
# 自动执行任务

# 5. 状态
@ai-dev-team status
# 输出：已完成 3/5，进行中 1，待验收 1
```

---

## 📈 性能

- **初始化:** <1 秒
- **分析:** 1-3 秒
- **规划:** <1 秒
- **状态查询:** <0.1 秒
- **内存:** ~50MB
- **磁盘:** ~1MB/项目

---

## 📄 License

GPL-3.0

---

*AI Dev Team v1.0.0 - 让 AI 自主开发和维护代码*
