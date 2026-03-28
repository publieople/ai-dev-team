#!/usr/bin/env python3
"""
AI Dev Team - OpenClaw Skill 入口

提供以下命令：
- @ai-dev-team init      - 初始化项目
- @ai-dev-team analyze   - 分析项目
- @ai-dev-team plan      - 生成开发规划
- @ai-dev-team start     - 开始开发循环
- @ai-dev-team status    - 查看状态
- @ai-dev-team approve   - 验收任务
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# 添加 scripts 目录到路径
script_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(script_dir))

def run_command(command: str, args: list):
    """运行主 Agent 命令"""
    from main_agent import MainAgent
    
    agent = MainAgent(".")
    
    if command == "init":
        return cmd_init(agent, args)
    elif command == "analyze":
        return cmd_analyze(agent, args)
    elif command == "plan":
        return cmd_plan(agent, args)
    elif command == "start":
        return cmd_start(agent, args)
    elif command == "status":
        return cmd_status(agent, args)
    elif command == "approve":
        return cmd_approve(agent, args)
    else:
        return {"error": f"未知命令：{command}"}

def cmd_init(agent, args):
    """初始化项目"""
    from init_project import init_project
    
    project_path = args[0] if args else "."
    init_project(project_path)
    
    return {
        "status": "success",
        "message": "项目初始化完成",
        "next_step": "运行 '@ai-dev-team analyze' 开始项目分析"
    }

def cmd_analyze(agent, args):
    """分析项目"""
    report = agent.analyze_project()
    
    return {
        "status": "success",
        "report": report,
        "message": f"项目分析完成，识别到 {len(report.get('potential_tasks', []))} 个潜在任务",
        "next_step": "运行 '@ai-dev-team plan' 生成开发规划"
    }

def cmd_plan(agent, args):
    """生成开发规划"""
    ai_dir = agent.ai_dir
    
    # 读取最近的分析报告
    reports_dir = ai_dir / "reports"
    analysis_reports = list(reports_dir.glob("project-analysis-*.md"))
    
    if not analysis_reports:
        return {
            "status": "error",
            "message": "未找到项目分析报告，请先运行 '@ai-dev-team analyze'"
        }
    
    # 获取最新报告
    latest_report = sorted(analysis_reports)[-1]
    
    # 读取分析的任务
    from state_manager import StateManager
    sm = StateManager(".")
    
    # 从分析报告中提取任务（简化处理）
    # 实际实现中应该解析 Markdown 或直接使用分析结果
    
    plan_file = reports_dir / f"dev-plan-{agent.state_manager._load() or 'v1'}.md"
    
    plan_content = f"""# 开发规划

**生成时间:** {agent.state_manager._load()}
**基于报告:** {latest_report.name}

---

## 任务列表

"""
    
    # 获取发现状态的任务
    discovered_tasks = sm.list_tasks()
    
    if not discovered_tasks:
        plan_content += "暂无待规划任务。\n\n"
    else:
        for i, task in enumerate(discovered_tasks[:10], 1):
            plan_content += f"""
### {i}. {task.get('title', '未命名任务')}

- **类型:** {task.get('type', 'unknown')}
- **优先级:** {task.get('priority', 'normal')}
- **描述:** {task.get('description', '无描述')}

"""
    
    plan_content += """
---

## 执行顺序

任务将按优先级依次执行：

1. 高优先级任务优先
2. 依赖关系自动排序
3. 每次只执行一个任务（避免冲突）

---

## 下一步

运行 `@ai-dev-team start` 开始开发循环。

*规划由 AI Dev Team 主 Agent 生成*
"""
    
    plan_file.write_text(plan_content, encoding="utf-8")
    
    return {
        "status": "success",
        "plan_file": str(plan_file),
        "task_count": len(discovered_tasks),
        "message": f"开发规划已生成，共 {len(discovered_tasks)} 个任务",
        "next_step": "运行 '@ai-dev-team start' 开始开发循环"
    }

def cmd_start(agent, args):
    """开始开发循环"""
    auto_approve = "--auto-approve" in args
    
    # 获取待处理任务
    from state_manager import StateManager, State
    sm = StateManager(".")
    
    pending_tasks = sm.list_tasks(State.PENDING_APPROVAL)
    discovered_tasks = sm.list_tasks(State.DISCOVERED)
    
    if not pending_tasks and not discovered_tasks:
        return {
            "status": "info",
            "message": "没有待处理的任务",
            "suggestion": "运行 '@ai-dev-team analyze' 发现新任务"
        }
    
    # 将发现的任务转为待批准
    for task in discovered_tasks:
        sm.transition(task["tid"], State.PENDING_APPROVAL)
    
    # 开始开发循环
    agent.run_development_cycle(auto_approve=auto_approve)
    
    return {
        "status": "success",
        "message": "开发循环已启动",
        "pending_tasks": len(pending_tasks) + len(discovered_tasks)
    }

def cmd_status(agent, args):
    """查看状态"""
    stats = agent.status()
    
    # 获取详细任务列表
    from state_manager import StateManager, State
    sm = StateManager(".")
    
    all_tasks = sm.list_tasks()
    
    status_by_state = {}
    for task in all_tasks:
        state = task.get("s", "unknown")
        if state not in status_by_state:
            status_by_state[state] = []
        status_by_state[state].append({
            "tid": task["tid"],
            "title": task.get("title", "未命名"),
            "type": task.get("type", "unknown")
        })
    
    return {
        "status": "success",
        "stats": stats,
        "tasks_by_state": status_by_state,
        "message": f"共 {stats['total']} 个任务，{stats['completed']} 已完成，{stats['active']} 进行中"
    }

def cmd_approve(agent, args):
    """验收任务"""
    # 解析参数
    task_id = None
    approved = True
    
    for arg in args:
        if arg.startswith("--task-id="):
            task_id = arg.split("=")[1]
        elif arg.startswith("--reject"):
            approved = False
    
    if not task_id:
        return {
            "status": "error",
            "message": "需要指定任务 ID，使用 --task-id=<id>"
        }
    
    agent.human_test_approval(task_id, approved)
    
    return {
        "status": "success",
        "task_id": task_id,
        "approved": approved,
        "message": f"任务 {task_id} 已{'批准' if approved else '拒绝'}"
    }

def main():
    """主入口"""
    # 解析命令
    if len(sys.argv) < 2:
        print("用法：@ai-dev-team <command> [args]")
        print("命令：init, analyze, plan, start, status, approve")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    try:
        result = run_command(command, args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
