# 设计文档

**任务 ID:** {{task_id}}
**设计者:** {{agent_id}}
**创建时间:** {{created_at}}
**版本:** {{version}}

---

## 概述

### 背景

{{background}}

### 目标

{{goals}}

### 范围

{{scope}}

---

## 技术方案

### 架构设计

{{architecture_diagram}}

### 核心组件

{{#components}}
#### {{name}}

**职责:** {{responsibility}}

**接口:**
```
{{interface}}
```

{{/components}}

### 数据流

{{data_flow}}

---

## 实现计划

### 阶段划分

{{#phases}}
#### 阶段 {{index}}: {{name}}

**任务:**
- {{tasks}}

**预计时间:** {{duration}}

{{/phases}}

### 依赖关系

{{dependencies}}

---

## 测试策略

### 单元测试

{{unit_tests}}

### 集成测试

{{integration_tests}}

### 验收标准

{{acceptance_criteria}}

---

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| {{risk}} | {{probability}} | {{impact}} | {{mitigation}} |

---

## 参考文档

- {{references}}

---

## 变更历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|----------|
| {{version}} | {{date}} | {{author}} | {{change}} |

---

*设计文档由 AI Dev Team Researcher Agent 生成*
