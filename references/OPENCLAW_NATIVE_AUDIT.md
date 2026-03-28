# OpenClaw 原生功能使用审计

**日期:** 2026-03-28  
**版本:** v1.1.0  
**状态:** ⚠️ 部分实现

---

## 📊 审计结果总览

| 模块 | OpenClaw 原生 | 独立实现 | 完成度 |
|------|--------------|----------|--------|
| **子 Agent 创建** | ✅ sessions_spawn | ❌ 占位符 | 50% |
| **工具调用** | ⚠️ 部分 | ❌ subprocess | 30% |
| **会话管理** | ❌ 未使用 | ❌ 无 | 0% |
| **通告机制** | ❌ 未使用 | ❌ 无 | 0% |
| **沙箱隔离** | ⚠️ 配置 | ❌ 未验证 | 50% |
| **Git 操作** | ❌ 未使用 | ✅ subprocess | 100% |
| **文件操作** | ❌ 未使用 | ✅ pathlib | 100% |

**总体完成度:** ~40%

---

## ❌ 未使用 OpenClaw 原生功能的部分

### 1. sessions_spawn 调用（关键）

**问题:** 主 Agent 中的 `sessions_spawn` 只是占位符

**当前代码:**
```python
# main_agent.py 第 427 行
def _execute_developer_agent(self, config: Dict) -> Dict:
    # ❌ 这只是模拟，没有真正调用 OpenClaw 工具
    spawn_result = {
        "status": "accepted",
        "runId": f"run-{int(time.time() * 1000)}",
        "childSessionKey": f"agent:ai-dev-team-developer:subagent:{config['task_id']}"
    }
    return spawn_result
```

**应该使用:**
```python
# ✅ 正确的 OpenClaw 工具调用
# 通过 OpenClaw 的 sessions_spawn 工具
result = sessions_spawn(
    task=prompt,
    agentId="ai-dev-team-developer",
    model="bailian/qwen3.5-plus",
    thinking="off",
    runTimeoutSeconds=7200,
    cleanup="delete"
)
```

**影响:** 
- ❌ 子 Agent 没有真正隔离
- ❌ 无法通过 `/subagents` 监控
- ❌ 没有通告机制
- ❌ 无法使用沙箱

**优先级:** 🔴 高

---

### 2. Context7 调用（严重）

**问题:** 使用 `subprocess` 调用 Context7，而不是 OpenClaw 工具

**当前代码:**
```python
# researcher_agent.py 第 31 行
def search_context7(self, library: str, query: str) -> Optional[Dict]:
    # ❌ 使用 subprocess 调用 npx 命令
    result = subprocess.run(
        ["npx", "tsx", "query.ts", "search", library, query],
        cwd=str(context7_dir),
        capture_output=True,
        text=True,
        timeout=30
    )
```

**应该使用:**
```python
# ✅ 使用 OpenClaw 的 web_search 工具或直接调用 Context7 MCP
# 通过 OpenClaw 工具系统
result = web_search(
    query=f"{library} {query}",
    count=5
)

# 或者使用 Context7 MCP 工具（如果已安装）
```

**影响:**
- ❌ 无法利用 OpenClaw 的认证管理
- ❌ 无法追踪工具调用
- ❌ 错误处理不完善

**优先级:** 🟡 中

---

### 3. Git 操作

**问题:** 使用 `subprocess` 调用 git 命令

**当前代码:**
```python
# git_wrapper.py 第 23 行
def run_git(args, cwd=None, check=True):
    # ❌ 使用 subprocess 调用 git
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check
    )
```

**应该使用:**
```python
# ✅ 使用 OpenClaw 的 exec 工具
result = exec(
    command=f"git {' '.join(args)}",
    cwd=cwd,
    timeout=60
)
```

**影响:**
- ⚠️ 较小（Git 操作本身没问题）
- ❌ 但无法利用 OpenClaw 的进程管理

**优先级:** 🟢 低

---

### 4. 文件操作

**问题:** 使用 Python 标准库，未使用 OpenClaw 工具

**当前代码:**
```python
# 所有 Agent 文件
content = filepath.read_text(encoding="utf-8")
filepath.write_text(content, encoding="utf-8")
```

**应该使用:**
```python
# ✅ 使用 OpenClaw 的 read/write 工具
content = read(path=str(filepath))
write(path=str(filepath), content=content)
```

**影响:**
- ⚠️ 较小（文件操作本身没问题）
- ❌ 但无法利用 OpenClaw 的沙箱和权限控制

**优先级:** 🟢 低

---

### 5. 测试执行

**问题:** 使用 `subprocess` 运行测试

**当前代码:**
```python
# tester_agent.py 第 129 行
def _run_pytest(self) -> Optional[Dict]:
    # ❌ 使用 subprocess 调用 pytest
    result = subprocess.run(
        ["pytest", "--tb=short"],
        cwd=str(self.project_path),
        capture_output=True,
        text=True,
        timeout=300
    )
```

**应该使用:**
```python
# ✅ 使用 OpenClaw 的 exec/process 工具
result = exec(
    command="pytest --tb=short",
    cwd=str(self.project_path),
    timeout=300,
    yieldMs=10000  # 10 秒后后台运行
)
```

**影响:**
- ❌ 无法利用 OpenClaw 的进程管理
- ❌ 无法查看实时日志

**优先级:** 🟡 中

---

### 6. 会话监控（完全缺失）

**问题:** 没有实现 `/subagents` 监控功能

**缺失功能:**
```bash
# ❌ 无法使用这些命令
/subagents list          # 查看子 Agent
/subagents log <id>      # 查看日志
/subagents info <id>     # 查看信息
/subagents kill <id>     # 停止子 Agent
```

**原因:**
- 子 Agent 没有真正使用 `sessions_spawn` 创建
- 没有独立的会话 ID

**优先级:** 🔴 高

---

### 7. 通告机制（完全缺失）

**问题:** 子 Agent 完成后没有自动通告

**缺失功能:**
```python
# ❌ 没有实现通告步骤
# 子 Agent 完成后应该：
# 1. 生成报告文件
# 2. 返回 ANNOUNCE 消息
# 3. OpenClaw 自动发布到主会话
```

**应该实现:**
```python
# ✅ 子 Agent 完成时
print("✅ 任务完成")
print(f"报告：{report_file}")
# OpenClaw 会自动捕获并通告
```

**优先级:** 🔴 高

---

## 🔧 需要重构的部分

### 优先级 1: 核心架构（必须）

#### 1.1 主 Agent 的 sessions_spawn 调用

**文件:** `scripts/main_agent.py`

**当前:**
```python
def _execute_developer_agent(self, config: Dict) -> Dict:
    # 占位符实现
    spawn_result = {...}
    return spawn_result
```

**需要:**
```python
def _execute_developer_agent(self, config: Dict) -> Dict:
    # 实际调用 OpenClaw sessions_spawn 工具
    # 这需要在 OpenClaw 环境中通过工具调用
    # Python 脚本中无法直接调用
    
    # 方案：返回配置，由 OpenClaw 主 Agent 调用
    return {
        "tool": "sessions_spawn",
        "params": {
            "task": config["prompt"],
            "agentId": "ai-dev-team-developer",
            "model": "bailian/qwen3.5-plus",
            "thinking": "off",
            "runTimeoutSeconds": 7200,
            "cleanup": "delete"
        }
    }
```

**难度:** 🔴 高  
**工作量:** 2-3 小时

---

#### 1.2 Researcher Agent 的文档收集

**文件:** `scripts/researcher_agent.py`

**当前:**
```python
def get_context7_context(self, library_id: str, query: str):
    result = subprocess.run(["npx", "tsx", "query.ts", ...])
```

**需要:**
```python
def get_context7_context(self, library_id: str, query: str):
    # 方案 1: 使用 OpenClaw web_search
    # 方案 2: 直接调用 Context7 API
    # 方案 3: 通过 OpenClaw MCP 工具
    
    # 推荐方案 3
    return {
        "tool": "context7_context",
        "params": {
            "libraryId": library_id,
            "query": query,
            "type": "txt"
        }
    }
```

**难度:** 🟡 中  
**工作量:** 1-2 小时

---

#### 1.3 Tester Agent 的测试执行

**文件:** `scripts/tester_agent.py`

**当前:**
```python
def _run_pytest(self):
    result = subprocess.run(["pytest", ...])
```

**需要:**
```python
def _run_pytest(self):
    return {
        "tool": "exec",
        "params": {
            "command": "pytest --tb=short",
            "cwd": str(self.project_path),
            "timeout": 300
        }
    }
```

**难度:** 🟢 低  
**工作量:** 30 分钟

---

### 优先级 2: 工具集成（重要）

#### 2.1 Git 操作封装

**文件:** `scripts/git_wrapper.py`

**当前:**
```python
def run_git(args, cwd=None):
    result = subprocess.run(["git"] + args, ...)
```

**需要:**
```python
def run_git(args, cwd=None):
    return {
        "tool": "exec",
        "params": {
            "command": f"git {' '.join(args)}",
            "cwd": cwd
        }
    }
```

**难度:** 🟢 低  
**工作量:** 30 分钟

---

#### 2.2 文件操作

**所有 Agent 文件**

**当前:**
```python
content = filepath.read_text()
filepath.write_text(content)
```

**需要:**
```python
# 在 OpenClaw 环境中
content = read(path=str(filepath))
write(path=str(filepath), content=content)
```

**难度:** 🟢 低  
**工作量:** 1 小时

---

### 优先级 3: 监控和通告（可选）

#### 3.1 会话监控

**需要实现:**
- `/subagents list` 集成
- 日志查看
- 会话信息管理

**难度:** 🟡 中  
**工作量:** 2 小时

---

#### 3.2 通告机制

**需要实现:**
- 子 Agent 完成报告
- 自动发布到主会话
- 结果汇总

**难度:** 🟡 中  
**工作量:** 1-2 小时

---

## 📋 重构方案

### 方案 A: 完全 OpenClaw 化（推荐）

**特点:**
- 所有工具调用通过 OpenClaw
- 真正的隔离子 Agent
- 完整监控和通告

**工作量:** 8-12 小时

**步骤:**
1. 重构 `main_agent.py` 使用 sessions_spawn
2. 重构所有工具调用为 OpenClaw 工具
3. 实现通告机制
4. 集成会话监控

---

### 方案 B: 混合模式（折中）

**特点:**
- 保留 Python 脚本（本地测试）
- 添加 OpenClaw 工具调用选项
- 通过配置切换

**工作量:** 4-6 小时

**步骤:**
1. 添加工具调用抽象层
2. 实现本地模式和 OpenClaw 模式
3. 配置文件切换

---

### 方案 C: 保持现状（不推荐）

**特点:**
- 继续使用 subprocess
- 简单直接
- 无法利用 OpenClaw 功能

**工作量:** 0 小时

**缺点:**
- ❌ 无隔离
- ❌ 无监控
- ❌ 无通告
- ❌ 无沙箱

---

## 🎯 建议

### 短期（本周）

1. **实现方案 B（混合模式）**
   - 保持本地测试能力
   - 添加 OpenClaw 工具调用
   - 验证核心功能

2. **优先级:**
   - 🔴 sessions_spawn 调用
   - 🟡 Context7 集成
   - 🟢 Git/文件操作

### 中期（本月）

1. **迁移到方案 A（完全 OpenClaw 化）**
   - 所有工具调用 OpenClaw 化
   - 实现完整监控
   - 实现通告机制

2. **测试和验证:**
   - 真实项目测试
   - 性能优化
   - 文档完善

---

## 📖 参考

- [OpenClaw sessions_spawn 文档](https://docs.openclaw.ai/zh-CN/tools/subagents)
- [OpenClaw 工具系统](https://docs.openclaw.ai/gateway/tools)
- [多 Agent 沙箱配置](https://docs.openclaw.ai/zh-CN/tools/multi-agent-sandbox-tools)

---

*AI Dev Team v1.1.0 - OpenClaw 原生功能审计*
