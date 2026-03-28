# 项目理解报告

> 生成时间: {{timestamp}}
> 主Agent: {{agent_id}}

## 项目概览

| 属性 | 值 |
|------|-----|
| 项目名称 | {{project_name}} |
| 项目路径 | {{project_path}} |
| 技术栈 | {{tech_stack}} |
| 项目类型 | {{project_type}} |

## 目录结构

```
{{directory_tree}}
```

## 关键文件

| 文件 | 说明 |
|------|------|
{{#key_files}}
| {{path}} | {{description}} |
{{/key_files}}

## 依赖分析

{{#dependencies}}
### {{type}}

{{#items}}
- {{name}} ({{version}})
{{/items}}

{{/dependencies}}

## 潜在优化点

{{#optimizations}}
### {{category}}

{{#items}}
- [ ] {{description}}
  - 优先级: {{priority}}
  - 预估工作量: {{effort}}
{{/items}}

{{/optimizations}}

## 建议的开发规划

{{#suggestions}}
1. **{{phase}}**
   {{#tasks}}
   - {{description}}
   {{/tasks}}

{{/suggestions}}

## 需要人类确认

{{#questions}}
- [ ] {{question}}
{{/questions}}

---

**下一步:** 请确认以上理解是否正确，或补充说明项目目标和优先级。
