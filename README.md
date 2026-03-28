# AI Dev Team

AI驱动的自主开发团队管理系统。

## 愿景

模拟真实软件公司架构：
- **人类 = 甲方**：验收成果、做最终决策
- **主Agent = CEO**：统筹规划、指派任务、不直接编码
- **子Agent = 员工**：执行具体开发任务，完成后销毁

## 核心特性

- **通用框架**：不绑定特定技术栈
- **状态机驱动**：清晰的任务生命周期管理
- **单任务单Agent**：资源节制，职责明确
- **Git可追溯**：所有AI提交带完整元数据
- **分层上报**：AI自主决策，必要时上报人类

## 快速开始

```bash
# 1. 在项目根目录初始化
@ai-dev-team init

# 2. 分析项目（主Agent生成理解报告）
@ai-dev-team analyze

# 3. 开始开发循环
@ai-dev-team start

# 4. 查看状态
@ai-dev-team status
```

## 目录结构

```
.ai-dev-team/
├── config.json          # 配置
├── state.json           # 状态机（TOON格式）
├── tasks/               # 任务卡片
├── reports/             # 执行报告
└── logs/                # Agent日志
```

## 状态机

```
DISCOVERED → ANALYZING → PLANNING → PENDING_APPROVAL → ASSIGNED 
                                                              ↓
COMPLETED ← TESTING ← IN_PROGRESS ←←←←←←←←←←←←←←←←←←←←←←┘
   ↓
git commit
```

## 配置

`.ai-dev-team/config.json`：

```json
{
  "workflow": {
    "auto_approve": false,      # 是否自动批准规划
    "require_human_test": true,  # 是否需要人类验收
    "max_retries": 3             # 最大重试次数
  },
  "git": {
    "auto_commit": true,         # 自动Git提交
    "traceability": true         # 启用可追溯
  }
}
```

## 文档

- [详细架构](references/architecture.md)
- [状态机定义](references/state-machine.md)
- [任务协议](references/task-protocol.md)
- [Agent类型](references/agent-types.md)
- [MVP实现](references/mvp-implementation.md)
- [故障排查](references/troubleshooting.md)

## 开发状态

**MVP阶段**：核心主Agent和子Agent流程已实现，待测试验证。

## License

MIT
