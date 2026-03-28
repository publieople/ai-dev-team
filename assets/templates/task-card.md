# 任务卡片: {{tid}}

| 属性 | 值 |
|------|-----|
| 任务ID | {{tid}} |
| 类型 | {{type}} |
| 优先级 | {{priority}} |
| 状态 | {{state}} |
| 创建时间 | {{created}} |
| 超时设置 | {{timeout}} |

## 任务描述

{{title}}

{{description}}

## 相关文件

{{#files}}
- `{{.}}`
{{/files}}

## 约束条件

{{#constraints}}
- {{.}}
{{/constraints}}

## 交付物

{{#deliverables}}
- [ ] {{.}}
{{/deliverables}}

## 参考文档

{{#references}}
- {{.}}
{{/references}}

---

**执行记录:**

{{#executions}}
### 尝试 {{attempt}}

- Agent: {{agent_id}}
- 状态: {{status}}
- 耗时: {{duration}}
- 结果: {{result}}

{{/executions}}
