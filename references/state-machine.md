# 状态机定义

## 状态列表

| 状态 | 代码 | 说明 |
|------|------|------|
| DISCOVERED | D | 自动发现的需求/问题 |
| ANALYZING | A | 主Agent分析中 |
| PLANNING | P | 生成开发规划中 |
| PENDING_APPROVAL | PA | 等待人类确认 |
| ASSIGNED | AS | 已指派子Agent |
| IN_PROGRESS | IP | 子Agent开发中 |
| TESTING | T | 测试中 |
| PENDING_HUMAN_TEST | PHT | 等待人类验收 |
| ESCALATED | E | 上报主Agent处理 |
| HUMAN_ESCALATION | HE | 需人类介入 |
| COMPLETED | C | 已完成 |
| CANCELLED | X | 已取消 |
| REASSIGNING | R | 重新指派中 |

## 状态转换

```
DISCOVERED
    ↓
ANALYZING ──→ HUMAN_ESCALATION (需人类决策)
    ↓
PLANNING
    ↓
PENDING_APPROVAL ──→ CANCELLED (人类拒绝)
    ↓ (人类确认 / auto_approve)
ASSIGNED
    ↓
IN_PROGRESS ──→ ESCALATED (重试超限)
    ↓ (完成)
TESTING ──→ IN_PROGRESS (测试失败)
    ↓ (通过)
PENDING_HUMAN_TEST ──→ ANALYZING (人类拒绝，带反馈)
    ↓ (人类通过)
COMPLETED ──→ git commit
```

## 重试机制

```yaml
IN_PROGRESS:
  失败 → retry_count += 1
  retry_count < max_retries → 回到 IN_PROGRESS
  retry_count >= max_retries → ESCALATED

ESCALATED:
  主Agent分析 → 能解决 → REASSIGNING → ASSIGNED
  主Agent分析 → 不能解决 → HUMAN_ESCALATION
```

## 存储格式

`.ai-dev-team/state.json` (TOON格式):

```json
{
  "v": 1,
  "tasks": {
    "t-abc123": {
      "s": "IP",
      "type": "feat",
      "pri": "high",
      "retry": 1,
      "agent": "dev-001",
      "created": 1711612800,
      "updated": 1711616400
    }
  },
  "queue": ["t-abc123", "t-def456"],
  "active": "t-abc123"
}
```

字段缩写（TOON优化）：
- `v`: version
- `s`: state
- `pri`: priority
- `t-`: task id prefix
- `feat`: feature
- `bug`: bugfix
- `ref`: refactor
