# AI Dev Team - AI 自主开发团队

> **v1.2.0** - 提示词驱动的自主开发团队（无需 Python 脚本）

---

## 🎯 这是什么？

AI Dev Team 是一个 **自主运行的 AI 开发团队**，模拟真实软件公司的运作：

- **人类** = 甲方（验收决策）
- **主 Agent** = CEO（统筹规划）
- **子 Agent** = 员工（Developer/Tester/Researcher）

主 Agent  autonomously 分析项目、规划任务、创建子 Agent 执行工作，人类只需在关键节点验收。

---

## 🌟 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 自主工作 | AI 自己判断何时分析、开发、测试 |
| 👥 多 Agent 协作 | 主 Agent 统筹，子 Agent 执行 |
| 📋 任务状态机 | 13 状态管理任务生命周期 |
| 🔍 自动文档 | Researcher Agent 收集官方文档 |
| ✅ 人类验收 | 关键节点等待人类批准 |
| 📝 Git 可追溯 | 所有提交带 AI 元数据 |
| ⏰ 定时验收 | 每天固定时间发送验收请求 |
| 🛡️ 沙箱隔离 | 子 Agent 在隔离环境执行 |
| 💬 提示词驱动 | 无需 Python 脚本，AI 直接调用工具 |

---

## 🚀 快速开始

### 5 分钟配置

```bash
# 1. 复制配置示例
cp skills/ai-dev-team/references/gateway.config.example.json ~/.openclaw/gateway.config.json

# 2. 编辑配置（添加 4 个 Agent）

# 3. 重启 Gateway
openclaw gateway restart

# 4. 在项目根目录初始化
cd /path/to/project
# 在 webchat 中发送：初始化 AI Dev Team
```

详细步骤见 **[QUICKSTART.md](QUICKSTART.md)**

---

## 🏗️ 架构

```
人类（甲方）
    ↑ ↓ 验收/决策/干涉
主 Agent（CEO）← 你在这里
    ↓ sessions_spawn
子 Agent（员工）
    ├─ Developer（开发）
    ├─ Tester（测试）
    └─ Researcher（文档）
```

### 主 Agent 职责

- 📊 项目分析
- 📋 任务规划
- 👥 创建子 Agent
- ✅ 验收审查
- 📢 上报人类

### 子 Agent 职责

| Agent | 职责 | 工具 |
|-------|------|------|
| Developer | 写代码、修复 Bug | read/write/edit/exec |
| Tester | 运行测试、审查代码 | read/exec（禁止写） |
| Researcher | 收集文档、写报告 | read/write/web_search |

---

## 📋 工作流

### 任务状态机

```
DISCOVERED → ANALYZING → PLANNING → PENDING_APPROVAL → ASSIGNED
                                                              ↓
COMPLETED ← TESTING ← IN_PROGRESS ←←←←←←←←←←←←←←←←←←←←←←┘

异常：IN_PROGRESS → 重试超限 → ESCALATED → 人类决策
```

### 开发循环

1. **分析项目** → 生成任务列表
2. **发送规划** → 等待人类批准
3. **创建子 Agent** → 执行任务
4. **审查报告** → 发送验收请求
5. **人类批准** → Git 提交
6. **继续下一个任务**

---

## 📁 目录结构

```
skills/ai-dev-team/
├── SKILL.md                  # 技能说明（主 Agent 提示词）
├── README.md                 # 本文档
├── QUICKSTART.md             # 快速开始指南
├── SETUP_AND_TEST.md         # 配置与测试指南
├── CHANGELOG.md              # 更新日志
├── agents/
│   ├── main/SOUL.md          # 主 Agent 人格
│   ├── developer/SOUL.md     # Developer Agent 人格
│   ├── tester/SOUL.md        # Tester Agent 人格
│   └── researcher/SOUL.md    # Researcher Agent 人格
├── scripts/
│   ├── init_project.py       # 项目初始化（可选）
│   ├── state_manager.py      # 状态机引擎（参考）
│   └── git_wrapper.py        # Git 封装（参考）
├── assets/
│   ├── configs/default.json  # 默认配置
│   └── templates/            # 报告模板
└── references/
    ├── architecture.md       # 架构设计
    ├── state-machine.md      # 状态机说明
    ├── task-protocol.md      # 任务协议
    ├── gateway.config.example.json  # 配置示例
    └── troubleshooting.md    # 故障排查
```

---

## 🛠️ 配置

### gateway.config.json

需要添加 4 个 Agent 配置：

```json
{
  "agents": {
    "list": [
      {
        "id": "ai-dev-team-main",
        "subagents": {
          "allowAgents": ["ai-dev-team-developer", "ai-dev-team-tester", "ai-dev-team-researcher"],
          "maxConcurrent": 1
        }
      },
      // ... 其他 3 个 Agent
    ]
  }
}
```

完整配置见 **[references/gateway.config.example.json](references/gateway.config.example.json)**

### 项目配置

`.ai-dev-team/config.json`：

```json
{
  "workflow": {
    "auto_approve": false,
    "require_human_test": true,
    "max_retries": 3
  },
  "review": {
    "schedule": "0 20 * * *",
    "timezone": "Asia/Shanghai"
  }
}
```

---

## 📝 使用示例

### 初始化项目

```
在 webchat 中发送：初始化 AI Dev Team
```

### 查看状态

```
当前项目状态如何？
```

### 验收任务

收到验收请求后回复：

```
批准
```

或

```
❌ 拒绝：功能不完整，需要添加错误处理
```

### 干涉开发

```
暂停当前任务，先修复 XXX Bug
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 5 分钟快速开始 |
| [SKILL.md](SKILL.md) | 技能说明（行为协议） |
| [references/architecture.md](references/architecture.md) | 详细架构设计 |
| [references/state-machine.md](references/state-machine.md) | 状态机说明 |
| [references/task-protocol.md](references/task-protocol.md) | 任务协议 |
| [references/gateway.config.example.json](references/gateway.config.example.json) | 配置示例 |

---

## ⚠️ 注意事项

### 安全边界

- ✅ 主 Agent 可访问全部工具
- ❌ 子 Agent 禁止访问 `gateway` / `cron`
- ❌ Developer 不能创建子 Agent
- ❌ Tester 不能修改代码

### 人类控制

- ⚠️ 新功能规划需要人类批准
- ⚠️ 架构级修改需要人类批准
- ❗ 任务失败 3 次必须上报

### 资源限制

- 一次只执行一个任务（`maxConcurrent: 1`）
- 子 Agent 超时自动终止（默认 2 小时）
- 会话 60 分钟后自动归档

---

## 🐛 故障排查

### 子 Agent 没有创建

检查 `gateway.config.json`：
- `subagents.allowAgents` 是否包含子 Agent ID
- `bindings` 配置是否正确

### 工具调用被拒绝

检查子 Agent 的 `tools.deny` 配置

### 验收提醒没有触发

检查 cron 配置，确认 Gateway 已重启

更多见 **[references/troubleshooting.md](references/troubleshooting.md)**

---

## 📊 实现状态

### ✅ v1.2.0 已完成

- [x] 提示词驱动的主 Agent（无需 Python 脚本）
- [x] 主 Agent 和子 Agent SOUL.md
- [x] sessions_spawn 集成指南
- [x] 状态机引擎
- [x] Git 可追溯提交
- [x] 报告系统
- [x] 配置示例

### ⏸️ 后续版本

- [ ] 心跳集成
- [ ] Context7 文档集成
- [ ] 多模态截图
- [ ] GitHub Actions 集成
- [ ] 多项目管理

---

## 🎓 设计理念

1. **AI 自主工作** - 不需要人类调用命令
2. **人类最终决策** - 关键节点等待验收
3. **透明可追溯** - Git 提交带元数据
4. **模块化设计** - 每个 Agent 职责清晰
5. **安全优先** - 子 Agent 沙箱隔离

---

## 📝 License

GPL-3.0

---

*AI Dev Team v1.1.0 - 让 AI 像真实公司一样运作*
