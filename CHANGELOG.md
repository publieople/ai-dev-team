# AI Dev Team - 更新日志

---

## v1.2.0 (2026-03-29) - 提示词驱动

### 🎯 重大变更

**主 Agent 架构重构** - 从 Python 脚本执行改为提示词驱动

**之前 (v1.1.0):**
- 主 Agent 逻辑在 `main_agent.py` 中
- Python 脚本无法调用 `sessions_spawn`
- 需要命令行触发（`@ai-dev-team init`）

**现在 (v1.2.0):**
- 主 Agent 逻辑在 `SKILL.md` 提示词中
- AI 直接在会话中调用 `sessions_spawn`
- AI 自主触发工作流（无需命令）

### ✨ 新增功能

- **提示词驱动** - SKILL.md = 完整的行为提示词
- **自主触发** - AI 根据场景自动判断何时工作
- **sessions_spawn 集成** - 主 Agent 可直接创建子 Agent
- **配置示例** - 完整的 `gateway.config.example.json`

### 📝 新增文件

- `SKILL.md` - 重写为主 Agent 提示词
- `agents/main/SOUL.md` - 主 Agent 人格（更新）
- `SETUP_AND_TEST.md` - 配置与测试指南
- `QUICKSTART.md` - 5 分钟快速开始
- `references/gateway.config.example.json` - 配置示例

### 🔄 更新文件

- `README.md` - 反映 v1.2.0 架构
- `agents/main/SOUL.md` - 与 SKILL.md 保持一致

### ⚠️ 废弃

- `index.py` - 命令行入口（不再需要）
- `scripts/main_agent.py` - 仅供参考
- `scripts/developer_agent.py` - 仅供参考
- `scripts/tester_agent.py` - 仅供参考
- `scripts/researcher_agent.py` - 仅供参考

**注意:** Python 脚本保留作为参考，但不再执行。

### 🎯 核心改进

| 方面 | v1.1.0 | v1.2.0 |
|------|--------|--------|
| 驱动方式 | Python 脚本 | 提示词 |
| sessions_spawn | ❌ 占位符 | ✅ 实际调用 |
| 触发方式 | 人类命令 | AI 自主 |
| 配置复杂度 | 中 | 低 |
| 学习成本 | 中 | 低 |

### 📊 需求对齐

v1.2.0 实现了以下需求：

- ✅ 主 Agent 自动读取项目
- ✅ AI 自行决定开发任务
- ✅ 创建/销毁子 Agent（sessions_spawn）
- ✅ 主 Agent 不直接工作
- ✅ 单次单任务
- ✅ 使用 subagents
- ✅ 通用框架
- ✅ 一主 Agent 一项目

### 🚀 使用方式

**v1.1.0:**
```bash
@ai-dev-team init
@ai-dev-team analyze
@ai-dev-team start
```

**v1.2.0:**
```
初始化 AI Dev Team
```
（AI 自主完成后续所有步骤）

---

## v1.1.0 (2026-03-28) - MVP

### ✅ 已完成

- 主 Agent 和子 Agent 框架
- 状态机引擎（13 状态）
- Git 可追溯提交
- 报告系统
- 配置示例

### ⚠️ 未完成

- sessions_spawn 实际调用（占位符）
- 心跳集成
- Context7 集成

---

## 未来版本

### v1.3.0 (计划中)

- [ ] 心跳集成
- [ ] Context7 文档集成
- [ ] 优化报告格式（HTML）

### v2.0.0 (愿景)

- [ ] 多模态截图
- [ ] GitHub Actions 集成
- [ ] 多项目管理
- [ ] 代码审查 Agent
- [ ] 自动化流程

---

*AI Dev Team - 让 AI 像真实公司一样运作*
