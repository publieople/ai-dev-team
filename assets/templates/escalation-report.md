# 问题上报

**上报时间:** {{timestamp}}
**任务 ID:** {{task_id}}
**上报级别:** {{level}}

---

## 任务信息

| 字段 | 值 |
|------|-----|
| 任务 ID | {{task_id}} |
| 任务类型 | {{task_type}} |
| 任务标题 | {{task_title}} |
| 优先级 | {{priority}} |
| 创建时间 | {{created_at}} |
| 重试次数 | {{retry_count}} |

---

## 问题描述

{{problem_description}}

---

## 已尝试的方案

{{#attempted_solutions}}
{{index}}. {{solution}}

{{/attempted_solutions}}

---

## 错误日志

```
{{error_logs}}
```

---

## 建议选项

### A. {{option_a_title}}

{{option_a_description}}

**优点:** {{option_a_pros}}
**缺点:** {{option_a_cons}}

### B. {{option_b_title}}

{{option_b_description}}

**优点:** {{option_b_pros}}
**缺点:** {{option_b_cons}}

### C. {{option_c_title}}

{{option_c_description}}

**优点:** {{option_c_pros}}
**缺点:** {{option_c_cons}}

---

## 需要人类决策

{{decision_needed}}

---

## 附件

- [执行报告]({{execution_report_url}})
- [相关提交]({{commits_url}})

---

*请回复 A/B/C 或提供具体指示*

*报告由 AI Dev Team 主 Agent 生成*
