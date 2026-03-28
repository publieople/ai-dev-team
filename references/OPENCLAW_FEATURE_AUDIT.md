# AI Dev Team 与 OpenClaw 功能对比审计

**日期:** 2026-03-28  
**版本:** v1.1.0  
**状态:** ⚠️ 部分实现

---

## 📊 总览

| 功能模块 | ai-dev-team 实现 | OpenClaw 原生 | 对应关系 | 优先级 |
|----------|------------------|---------------|----------|--------|
| **子 Agent 创建** | ❌ 占位符 | ✅ sessions_spawn | 未实现 | 🔴 高 |
| **命令执行** | ❌ subprocess | ✅ exec 工具 | 重复实现 | 🟡 中 |
| **文件操作** | ❌ pathlib | ✅ read/write/edit | 重复实现 | 🟢 低 |
| **Git 操作** | ❌ subprocess | ✅ exec 工具 | 重复实现 | 🟢 低 |
| **测试执行** | ❌ subprocess | ✅ exec/process | 重复实现 | 🟡 中 |
| **Context7 调用** | ❌ npx 命令 | ✅ web_search | 重复实现 | 🟡 中 |
| **沙箱隔离** | ⚠️ 配置 | ✅ Docker/SSH | 依赖配置 | 🔴 高 |
| **工具策略** | ⚠️ 配置 | ✅ allow/deny | 依赖配置 | 🔴 高 |
| **会话监控** | ❌ 无 | ✅ /subagents | 未实现 | 🔴 高 |
| **通告机制** | ❌ 无 | ✅ announce | 未实现 | 🔴 高 |

**总体评估:** 40% 功能使用 OpenClaw 原生，60% 重复实现

---

## 🔴 高优先级：关键差距

### 1. sessions_spawn 调用（核心架构）

**OpenClaw 官方实现:**

```python
# ✅ 正确的 OpenClaw 工具调用
result = sessions_spawn(
    task="你是一个 Developer Agent，任务如下：...",
    agentId="ai-dev-team-developer",
    model="bailian/qwen3.5-plus",
    thinking="off",
    runTimeoutSeconds=7200,
    cleanup="delete"
)
```

**ai-dev-team 当前实现:**

```python
# ❌ 占位符实现（main_agent.py 第 427 行）
def _execute_developer_agent(self, config: Dict) -> Dict:
    spawn_result = {
        "status": "accepted",
        "runId": f"run-{int(time.time() * 1000)}",
        "childSessionKey": f"agent:ai-dev-team-developer:subagent:{config['task_id']}"
    }
    return spawn_result
```

**差距:**
- ❌ 没有实际调用 `sessions_spawn` 工具
- ❌ 子 Agent 没有独立会话
- ❌ 无法通过 `/subagents` 监控
- ❌ 没有通告机制
- ❌ 无法使用沙箱隔离

**影响:** 这是从"简化版"到"原生版"的关键一步

**工作量:** 2-3 小时

---

### 2. 会话监控（/subagents）

**OpenClaw 官方功能:**

```bash
# 查看所有子 Agent
/subagents list

# 查看日志
/subagents log <id> 50

# 查看信息
/subagents info <id>

# 停止子 Agent
/subagents kill <id>

# 发送消息
/subagents send <id> "请加快进度"

# 指导方向
/subagents steer <id> "优先实现核心功能"
```

**ai-dev-team 当前实现:**
- ❌ 完全缺失

**影响:**
- 无法监控子 Agent 状态
- 无法查看实时日志
- 无法干预子 Agent

**工作量:** 1-2 小时（主要是集成）

---

### 3. 通告机制（Announce）

**OpenClaw 官方实现:**

```python
# 子 Agent 完成后自动通告
# OpenClaw 会自动捕获并发布到主会话

# 通告格式:
Status: success
Result: 任务完成摘要
Notes: 
  - runtime 5m12s
  - tokens 1234/567
  - cost $0.0012
  - sessionKey: agent:xxx:subagent:yyy
```

**ai-dev-team 当前实现:**
- ❌ 完全缺失
- ❌ 子 Agent 完成后没有自动报告

**影响:**
- 主 Agent 无法自动获知子 Agent 完成
- 需要轮询或手动检查

**工作量:** 1 小时（主要是理解机制）

---

### 4. 沙箱隔离配置

**OpenClaw 官方实现:**

```json5
{
  "agents": {
    "list": [
      {
        "id": "ai-dev-team-developer",
        "sandbox": {
          "mode": "all",      // 所有操作在沙箱中
          "scope": "session", // 每会话一个沙箱
          "backend": "docker" // Docker 后端
        }
      }
    ]
  }
}
```

**沙箱模式:**
- `"off"` - 无沙箱
- `"non-main"` - 非主会话沙箱
- `"all"` - 所有会话沙箱

**沙箱范围:**
- `"session"` - 每会话一个容器
- `"agent"` - 每 Agent 一个容器
- `"shared"` - 共享容器

**ai-dev-team 当前实现:**
- ⚠️ 配置文件中已设置
- ❌ 但未验证是否生效
- ❌ 没有测试沙箱环境

**工作量:** 1 小时（测试和验证）

---

### 5. 工具策略配置

**OpenClaw 官方实现:**

```json5
{
  "tools": {
    "allow": ["read", "write", "edit", "exec"],
    "deny": ["gateway", "cron", "sessions_*"]
  },
  "subagents": {
    "tools": {
      "deny": ["gateway", "cron"]  // 子 Agent 禁止访问
    }
  }
}
```

**工具组:**
- `group:fs` - 文件操作 (read, write, edit, apply_patch)
- `group:runtime` - 命令执行 (exec, bash, process)
- `group:sessions` - 会话管理 (sessions_*)
- `group:web` - 网络搜索 (web_search, web_fetch)

**ai-dev-team 当前实现:**
- ⚠️ 配置文件中已设置
- ❌ 但未验证是否生效

**工作量:** 30 分钟（测试和验证）

---

## 🟡 中优先级：重复实现

### 1. 命令执行（exec）

**OpenClaw 官方工具:**

```python
# ✅ 使用 OpenClaw exec 工具
result = exec(
    command="pytest --tb=short",
    cwd=str(project_path),
    timeout=300,
    yieldMs=10000  # 10 秒后后台运行
)
```

**ai-dev-team 当前实现:**

```python
# ❌ 使用 subprocess（tester_agent.py 第 129 行）
def _run_pytest(self):
    result = subprocess.run(
        ["pytest", "--tb=short"],
        cwd=str(self.project_path),
        capture_output=True,
        text=True,
        timeout=300
    )
```

**差距:**
- ❌ 无法利用 OpenClaw 的进程管理
- ❌ 无法查看实时日志
- ❌ 无法使用后台执行

**工作量:** 1 小时

---

### 2. Context7 调用

**OpenClaw 官方方式:**

```python
# ✅ 使用 web_search 工具
result = web_search(
    query=f"{library} {query}",
    count=5
)

# 或使用 Context7 MCP（如果已安装）
```

**ai-dev-team 当前实现:**

```python
# ❌ 使用 subprocess 调用 npx（researcher_agent.py 第 31 行）
def search_context7(self, library: str, query: str):
    result = subprocess.run(
        ["npx", "tsx", "query.ts", "search", library, query],
        cwd=str(context7_dir),
        capture_output=True,
        text=True,
        timeout=30
    )
```

**差距:**
- ❌ 无法利用 OpenClaw 的认证管理
- ❌ 无法追踪工具调用
- ❌ 错误处理不完善

**工作量:** 1-2 小时

---

### 3. 测试执行

**OpenClaw 官方方式:**

```python
# ✅ 使用 exec/process 工具
result = exec(
    command="npm test",
    cwd=str(project_path),
    timeout=300,
    background=False
)

# 后台执行
result = exec(
    command="pytest",
    timeout=600,
    yieldMs=10000  # 10 秒后后台
)

# 查看日志
process(action="log", sessionId="xxx", limit=50)
```

**ai-dev-team 当前实现:**
- ❌ 使用 subprocess
- ❌ 无法查看实时日志
- ❌ 无法后台执行

**工作量:** 1 小时

---

## 🟢 低优先级：可以保留

### 1. 文件操作（pathlib）

**OpenClaw 官方工具:**

```python
# ✅ 使用 read/write 工具
content = read(path="file.txt")
write(path="file.txt", content="new content")
edit(path="file.txt", oldText="old", newText="new")
```

**ai-dev-team 当前实现:**

```python
# 使用 pathlib（可以保留）
content = filepath.read_text(encoding="utf-8")
filepath.write_text(content, encoding="utf-8")
```

**评估:**
- ✅ 功能正常
- ⚠️ 但无法利用 OpenClaw 的沙箱和权限控制
- 🟢 **建议:** 保持现状（改动收益低）

---

### 2. Git 操作

**OpenClaw 官方方式:**

```python
# ✅ 使用 exec 工具
result = exec(
    command=f"git commit -m '{message}'",
    cwd=str(project_path)
)
```

**ai-dev-team 当前实现:**

```python
# 使用 subprocess（git_wrapper.py 第 23 行）
def run_git(args, cwd=None):
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True
    )
```

**评估:**
- ✅ 功能正常
- ⚠️ 但无法利用 OpenClaw 的进程管理
- 🟢 **建议:** 保持现状（改动收益低）

---

## 📋 重构优先级

### 阶段 1: 核心架构（必须）

| 任务 | 工作量 | 优先级 |
|------|--------|--------|
| 1.1 实现 sessions_spawn 调用 | 2-3 小时 | 🔴 高 |
| 1.2 集成会话监控 | 1-2 小时 | 🔴 高 |
| 1.3 实现通告机制 | 1 小时 | 🔴 高 |
| 1.4 验证沙箱配置 | 1 小时 | 🔴 高 |
| 1.5 验证工具策略 | 30 分钟 | 🔴 高 |

**小计:** 6-8 小时

---

### 阶段 2: 工具集成（重要）

| 任务 | 工作量 | 优先级 |
|------|--------|--------|
| 2.1 重构 Context7 调用 | 1-2 小时 | 🟡 中 |
| 2.2 重构测试执行 | 1 小时 | 🟡 中 |
| 2.3 重构命令执行 | 1 小时 | 🟡 中 |

**小计:** 3-4 小时

---

### 阶段 3: 优化（可选）

| 任务 | 工作量 | 优先级 |
|------|--------|--------|
| 3.1 文件操作 OpenClaw 化 | 1 小时 | 🟢 低 |
| 3.2 Git 操作 OpenClaw 化 | 30 分钟 | 🟢 低 |

**小计:** 1.5 小时

---

## 🎯 重构方案

### 方案 A: 完全 OpenClaw 化（推荐）

**特点:**
- ✅ 所有工具调用通过 OpenClaw
- ✅ 真正的隔离子 Agent
- ✅ 完整监控和通告
- ✅ 沙箱和工具策略生效

**工作量:** 10-12 小时

**步骤:**
1. 重构 `main_agent.py` 使用 `sessions_spawn`
2. 重构所有工具调用为 OpenClaw 工具
3. 实现通告机制
4. 集成会话监控
5. 验证沙箱和工具策略

---

### 方案 B: 混合模式（折中）✅ **当前采用**

**特点:**
- ✅ 保留 Python 脚本（本地测试）
- ✅ 添加 OpenClaw 工具调用选项
- ✅ 通过配置切换
- ⚠️ sessions_spawn 是占位符

**工作量:** 4-6 小时（需完成阶段 1）

**步骤:**
1. 实现真正的 `sessions_spawn` 调用
2. 添加工具调用抽象层
3. 实现本地模式和 OpenClaw 模式
4. 配置文件切换

---

### 方案 C: 保持现状（不推荐）

**特点:**
- ❌ 继续使用 subprocess
- ❌ 无法利用 OpenClaw 功能
- ❌ 无隔离、无监控、无通告

**工作量:** 0 小时

**缺点:**
- ❌ 无隔离
- ❌ 无监控
- ❌ 无通告
- ❌ 无沙箱
- ❌ 工具策略不生效

---

## 📖 参考文档

### OpenClaw 官方文档

- [`docs/tools/subagents.md`](file:///C:/Users/Publieople/.openclaw/workspace/openclaw-docs/docs/tools/subagents.md) - 子 Agent 系统
- [`docs/tools/exec.md`](file:///C:/Users/Publieople/.openclaw/workspace/openclaw-docs/docs/tools/exec.md) - 执行命令
- [`docs/gateway/sandboxing.md`](file:///C:/Users/Publieople/.openclaw/workspace/openclaw-docs/docs/gateway/sandboxing.md) - 沙箱隔离
- [`docs/tools/index.md`](file:///C:/Users/Publieople/.openclaw/workspace/openclaw-docs/docs/tools/index.md) - 工具系统总览

### 中文文档

- [`docs/zh-CN/tools/subagents.md`](file:///C:/Users/Publieople/.openclaw/workspace/openclaw-docs/docs/zh-CN/tools/subagents.md) - 子 Agent（中文）
- [`docs/zh-CN/tools/exec.md`](file:///C:/Users/Publieople/.openclaw/workspace/openclaw-docs/docs/zh-CN/tools/exec.md) - 执行命令（中文）

---

## ✅ 验收清单

### 阶段 1（核心架构）

- [ ] 实现真正的 `sessions_spawn` 调用
- [ ] 子 Agent 可通过 `/subagents list` 查看
- [ ] 子 Agent 完成后自动通告
- [ ] 沙箱配置生效
- [ ] 工具策略生效

### 阶段 2（工具集成）

- [ ] Context7 使用 OpenClaw 工具调用
- [ ] 测试执行使用 `exec/process`
- [ ] 命令执行使用 `exec`

### 阶段 3（优化）

- [ ] 文件操作使用 `read/write/edit`
- [ ] Git 操作使用 `exec`

---

*AI Dev Team v1.1.0 - OpenClaw 功能对比审计*
