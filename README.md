# AI Dev Team

> **v1.2.0** - 提示词驱动的自主开发团队

AI 驱动的自主开发团队管理系统。主 Agent 统筹规划，使用 `sessions_spawn` 创建子 Agent（Developer/Tester/Researcher）执行具体任务。

## 快速开始

### 1. 配置 Gateway

复制 `references/gateway.config.example.json` 到 `~/.openclaw/gateway.config.json`，添加 4 个 Agent。

### 2. 重启 Gateway

```bash
openclaw gateway restart
```

### 3. 初始化项目

在 webchat 中发送：

```
初始化 AI Dev Team
```

详细步骤见 **[docs/QUICKSTART.md](docs/QUICKSTART.md)**

## 核心特性

- 🤖 **自主工作** - AI 自己判断何时分析、开发、测试
- 👥 **多 Agent 协作** - 主 Agent 统筹，子 Agent 执行
- 📋 **任务状态机** - 13 状态管理任务生命周期
- ✅ **人类验收** - 关键节点等待人类批准
- 📝 **Git 可追溯** - 所有提交带 AI 元数据
- 💬 **提示词驱动** - 无需 Python 脚本，AI 直接调用工具

## 架构

```
人类（甲方）
    ↑ ↓ 验收/决策/干涉
主 Agent（CEO）
    ↓ sessions_spawn
子 Agent（员工）
    ├─ Developer（开发）
    ├─ Tester（测试）
    └─ Researcher（文档）
```

## 使用场景

- 自主开发和维护 Git 仓库
- 日常代码优化和重构
- Bug 修复和新特性开发
- 技术债务管理

## 配置示例

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

### 定时验收

```json
{
  "cron": {
    "jobs": [
      {
        "id": "ai-dev-team-daily-review",
        "schedule": {
          "kind": "cron",
          "expr": "0 20 * * *"
        },
        "payload": {
          "kind": "systemEvent",
          "text": "【定时验收提醒】现在是每日验收时间（20:00）"
        },
        "sessionTarget": "main"
      }
    ]
  }
}
```

## 文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | 技能说明（主 Agent 提示词） |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | 5 分钟快速开始 |
| [docs/SETUP_AND_TEST.md](docs/SETUP_AND_TEST.md) | 配置与测试指南 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 更新日志 |
| [references/gateway.config.example.json](references/gateway.config.example.json) | Gateway 配置示例 |

## 监控

```bash
# 查看子 Agent
/subagents list

# 查看日志
/subagents log dev-001

# 查看项目状态
cat .ai-dev-team/state.json
```

## License

GPL-3.0
