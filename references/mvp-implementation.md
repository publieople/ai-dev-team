# MVP实现指南

## 目标

使用OpenClaw现有功能（subagents、cron、文件系统）实现核心流程：
1. 主Agent分析项目并生成规划
2. 指派子Agent完成开发任务
3. 验收和Git提交流程

## 核心流程实现

### 1. 项目初始化

**主Agent执行：**

```python
# 检查Git仓库
# 创建 .ai-dev-team/ 目录
# 复制默认配置
# 生成项目分析报告
```

**OpenClaw工具：**
- `exec` 运行 init_project.py
- `read` 读取项目文件
- `write` 创建报告

### 2. 需求对齐

**主Agent执行：**

```
1. 读取项目结构
   - 扫描文件目录
   - 识别技术栈（package.json, requirements.txt等）
   - 分析代码复杂度

2. 生成《项目理解报告》
   - 使用模板填充
   - 列出潜在优化点

3. 等待人类确认
   - 呈现报告
   - 人类回复确认/修改

4. 创建初始任务队列
   - 将确认的优化点转为任务
   - 写入 state.json
```

### 3. 开发循环（核心）

```
主Agent循环:
    while True:
        # 1. 检查任务队列
        task = state_manager.get_next_task()
        
        if not task:
            # 发现新任务
            task = analyze_project_for_new_tasks()
            if not task:
                break  # 无任务，结束循环
        
        # 2. 生成规划（如果需要）
        if task['state'] == 'DISCOVERED':
            plan = generate_plan(task)
            task['state'] = 'PENDING_APPROVAL'
            present_plan_to_human(plan)
            wait_for_human_approval()
        
        # 3. 指派子Agent
        if task['state'] == 'ASSIGNED':
            # 使用 sessions_spawn 创建子Agent
            spawn_developer_agent(task)
        
        # 4. 等待子Agent完成
        result = wait_for_agent_completion()
        
        # 5. 验收
        if result['status'] == 'success':
            if verify_changes(result):
                task['state'] = 'PENDING_HUMAN_TEST'
                present_for_human_test()
            else:
                task['retry'] += 1
                if task['retry'] >= MAX_RETRIES:
                    task['state'] = 'ESCALATED'
                else:
                    task['state'] = 'ASSIGNED'  # 重试
        else:
            task['retry'] += 1
            # 失败处理...
        
        # 6. 人类验收
        if human_approves():
            git_commit(task, result)
            task['state'] = 'COMPLETED'
        else:
            task['state'] = 'ANALYZING'  # 带反馈重新分析
```

### 4. 子Agent实现

**使用 sessions_spawn：**

```python
# 主Agent创建子Agent
result = sessions_spawn(
    task="""
    你是一个Developer Agent，任务如下：
    
    任务ID: {task_id}
    类型: {task_type}
    描述: {description}
    
    相关文件: {files}
    约束条件: {constraints}
    
    你需要：
    1. 读取相关代码文件
    2. 理解任务需求
    3. 实现功能
    4. 运行测试
    5. 生成执行报告
    
    完成后，将报告写入 .ai-dev-team/reports/execution-{task_id}.md
    """,
    runtime="subagent",
    mode="run",
    timeoutSeconds=7200  # 2小时
)
```

**子Agent执行流程：**

```python
# 1. 读取任务卡片
task = read_task_card(task_id)

# 2. 读取代码上下文
for file in task['context']['files']:
    code = read(file)
    analyze(code)

# 3. 执行开发
implement_task()

# 4. 自测
run_tests()

# 5. 生成报告
write_execution_report()
```

### 5. 状态管理

**使用JSON文件：**

```python
# state.json 结构（TOON格式）
{
  "v": 1,
  "tasks": {
    "t-abc123": {
      "s": "IP",           # state
      "type": "feat",      # feature/bugfix/refactor
      "pri": "high",       # priority
      "retry": 1,          # retry count
      "agent": "dev-001",  # assigned agent
      "ct": 1711612800,    # created time
      "ut": 1711616400     # updated time
    }
  },
  "queue": ["t-abc123", "t-def456"],
  "active": "t-abc123"
}
```

**操作封装：**
- `state_manager.py` 提供读写接口
- 每次状态变更立即持久化
- 主Agent启动时加载状态

### 6. Git可追溯

**提交封装：**

```python
# git_wrapper.py
def ai_commit(message, task_id, agent_id):
    full_message = f"""
[AI-{task_id}] {message}

AI-Task: {task_id}
AI-Agent: {agent_id}
AI-Time: {iso_timestamp}
"""
    git commit -m full_message
```

**查询：**
```bash
git log --grep="[AI-"
git log --grep="AI-Task: t-abc123"
```

### 7. 上报机制

**上报条件：**

```python
def should_escalate(task):
    # 重试超限
    if task['retry'] >= MAX_RETRIES:
        return True
    
    # 连续失败
    recent_failures = count_recent_failures(task['type'])
    if recent_failures >= CONSECUTIVE_THRESHOLD:
        return True
    
    # 系统性异常（由主Agent判断）
    if is_systemic_issue(task):
        return True
    
    return False
```

**上报格式：**

```markdown
## 问题上报

**任务:** {task_id}
**类型:** {task_type}
**失败次数:** {retry_count}

**现象:**
{error_description}

**已尝试:**
{attempted_solutions}

**建议选项:**
A. {option_a}
B. {option_b}

**需要人类决策:**
{specific_question}
```

## 文件交互图

```
主Agent
  ├── 读取 → 项目文件
  ├── 读取/写入 → .ai-dev-team/state.json
  ├── 写入 → .ai-dev-team/reports/*.md
  ├── 执行 → git_wrapper.py
  └── 创建 → 子Agent (sessions_spawn)

子Agent
  ├── 读取 → 任务卡片
  ├── 读取 → 项目代码
  ├── 修改 → 项目代码
  ├── 执行 → 测试
  └── 写入 → 执行报告

人类
  ├── 读取 → 项目理解报告
  ├── 读取 → 开发规划
  ├── 读取 → 执行报告
  └── 回复 → 确认/反馈
```

## MVP功能清单

### 已实现（脚本）

- [x] init_project.py - 项目初始化
- [x] state_manager.py - 状态机管理
- [x] git_wrapper.py - Git可追溯封装

### 需主Agent实现

- [ ] 项目分析流程
- [ ] 任务生成逻辑
- [ ] 子Agent指派
- [ ] 验收判断
- [ ] 上报决策

### 需子Agent实现

- [ ] 任务执行流程
- [ ] 报告生成

## 下一步

1. 在真实项目中测试初始化流程
2. 实现第一个端到端开发任务
3. 迭代优化状态机和上报逻辑
