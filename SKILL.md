---
name: ai-dev-team
description: |
  AI驱动的自主开发团队管理系统。主Agent作为项目经理分析需求、拆分任务并指派子Agent执行开发，
  支持需求对齐、任务状态跟踪、自动验收和Git可追溯提交。
  
  使用场景：
  1. 初始化AI开发团队接管项目
  2. 主Agent分析项目并生成开发规划
  3. 指派子Agent执行具体开发任务
  4. 任务验收与Git提交管理
  5. 状态跟踪与上报决策
---

# AI Dev Team - 自主开发团队

> **AI软件公司模拟系统** - 主Agent统筹，子Agent执行，人类最终验收

## 核心架构

```
人类（甲方）
    ↓ 需求对齐 / 验收确认
主Agent（CEO）- 单项目专注
    ├─ 项目分析 → 生成规划
    ├─ 任务拆分 → 状态机管理
    ├─ 指派子Agent（单任务单Agent）
    ├─ 验收评估 → Git提交
    └─ 异常上报 → 人类决策
        ↓
    子Agent（员工）- 执行后销毁
        ├─ 读取上下文
        ├─ 执行任务
        └─ 生成报告
```

## 快速开始

### 1. 初始化项目

```bash
# 在项目根目录执行
@ai-dev-team init
```

主Agent将：
1. 分析项目结构和技术栈
2. 生成《项目理解报告》
3. 等待人类确认/修正

### 2. 开始开发循环

```bash
@ai-dev-team start
```

主Agent将：
1. 识别待优化/开发点
2. 生成任务规划
3. 等待人类确认（可配置auto_approve）
4. 指派子Agent执行
5. 验收结果 → Git提交

### 3. 查看状态

```bash
@ai-dev-team status
```

## 状态机

```yaml
DISCOVERED → ANALYZING → PLANNING → PENDING_APPROVAL → ASSIGNED 
                                                              ↓
COMPLETED ← TESTING ← IN_PROGRESS ←←←←←←←←←←←←←←←←←←←←←←┘
   ↓
git commit
```

**异常分支：**
- `IN_PROGRESS` → 重试超限 → `ESCALATED` → 主Agent决策/上报人类
- `PENDING_APPROVAL` → 人类拒绝 → `CANCELLED`

## 任务卡片协议

每个任务以标准化卡片形式传递：

```json
{
  "tid": "task-uuid",
  "type": "feature|bugfix|refactor|test|doc",
  "priority": "critical|high|normal|low",
  "context": {
    "files": ["src/auth.ts"],
    "description": "添加用户认证",
    "constraints": ["使用JWT", "支持刷新token"]
  },
  "deliverables": ["实现代码", "单元测试"],
  "max_retries": 3,
  "timeout": "2h"
}
```

## Git可追溯

所有AI提交包含元数据：

```
[AI-<tid>] <type>: <description>

AI-Task: <tid>
AI-Agent: <agent-id>
AI-Plan: <plan-file>
AI-Report: <report-file>
```

查询：
```bash
git log --grep="AI-"
git log --grep="AI-Task: task-uuid"
```

## 配置

项目根目录 `.ai-dev-team/config.json`：

```json
{
  "auto_approve": false,
  "max_concurrent_agents": 1,
  "default_timeout": "2h",
  "report_format": "markdown",
  "escalation_threshold": 3
}
```

## 上报机制

主Agent遇到以下情况上报人类：
- 连续3次同类型任务失败
- 超出主Agent决策能力
- 系统性异常信号

上报格式：《问题报告》包含：
- 问题描述
- 已尝试方案
- 建议选项
- 需要人类决策的点

## 参考文档

- [详细架构](references/architecture.md)
- [状态机定义](references/state-machine.md)
- [任务协议](references/task-protocol.md)
- [Agent类型](references/agent-types.md)
- [故障排查](references/troubleshooting.md)

## 依赖

- OpenClaw subagents 功能
- 项目使用Git版本控制
