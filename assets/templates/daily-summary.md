# 每日开发总结

**日期:** {{date}}
**项目:** {{project_name}}
**主 Agent:** {{main_agent_id}}

---

## 今日概览

| 指标 | 数值 |
|------|------|
| 新发现任务 | {{new_discovered}} |
| 已完成任务 | {{completed}} |
| 进行中任务 | {{in_progress}} |
| 上报任务 | {{escalated}} |
| Git 提交数 | {{commits}} |

---

## 完成任务

{{#completed_tasks}}
### {{title}}

- **任务 ID:** {{tid}}
- **类型:** {{type}}
- **Agent:** {{agent_id}}
- **提交:** {{commit_hash}}

{{/completed_tasks}}

---

## 进行中任务

{{#in_progress_tasks}}
### {{title}}

- **任务 ID:** {{tid}}
- **类型:** {{type}}
- **当前状态:** {{state}}
- **预计完成:** {{eta}}

{{/in_progress_tasks}}

---

## 需要关注

### 上报任务

{{#escalated_tasks}}
- **{{title}}** ({{tid}}): {{reason}}

{{/escalated_tasks}}

### 失败任务

{{#failed_tasks}}
- **{{title}}** ({{tid}}): 失败 {{retry_count}} 次

{{/failed_tasks}}

---

## 明日计划

{{tomorrow_plan}}

---

## 备注

{{notes}}

---

*报告由 AI Dev Team 主 Agent 自动生成*
