# 执行报告

> 任务ID: {{tid}}
> 执行Agent: {{agent_id}}
> 完成时间: {{completed_at}}

## 执行摘要

{{summary}}

## 代码变更

### 修改的文件

{{#changes.modified}}
- `{{.}}`
{{/changes.modified}}

### 新增的文件

{{#changes.created}}
- `{{.}}`
{{/changes.created}}

### 删除的文件

{{#changes.deleted}}
- `{{.}}`
{{/changes.deleted}}

## 测试结果

{{#tests}}
| 指标 | 数值 |
|------|-----|
| 运行测试 | {{run}} |
| 通过 | {{passed}} |
| 失败 | {{failed}} |
| 覆盖率 | {{coverage}} |

{{/tests}}

## 遇到的问题

{{#issues}}
### {{title}}

{{description}}

**解决方案:** {{solution}}

{{/issues}}

{{^issues}}
无
{{/issues}}

## 改进建议

{{#suggestions}}
- {{.}}
{{/suggestions}}

{{^suggestions}}
无
{{/suggestions}}

## 耗时统计

- 总耗时: {{time_spent}}
- 代码编写: {{time_coding}}
- 测试调试: {{time_testing}}

---

**状态:** {{status}}
