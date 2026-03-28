#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Dev Team - 命令行入口
通过 OpenClaw 调用
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime

# 添加脚本目录到路径
script_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(script_dir))

from main_agent import MainAgent
from state_manager import State

def cmd_init(args):
    """初始化项目"""
    print("🚀 初始化 AI Dev Team 项目...\n")
    
    project_path = Path(args.path).resolve()
    ai_dir = project_path / ".ai-dev-team"
    
    # 检查是否是 Git 仓库
    if not (project_path / ".git").exists():
        print("⚠️  警告：当前目录不是 Git 仓库")
        response = input("是否继续？(y/n): ").strip().lower()
        if response != 'y':
            print("已取消")
            return
    
    # 创建目录结构
    dirs = ["tasks", "reports", "docs", "logs"]
    for d in dirs:
        (ai_dir / d).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建目录：.ai-dev-team/{d}/")
    
    # 复制默认配置
    default_config = Path(__file__).parent / "assets" / "configs" / "default.json"
    if default_config.exists():
        config_content = default_config.read_text(encoding="utf-8")
        # 更新项目名称
        config = json.loads(config_content)
        config["project"]["name"] = project_path.name
        config["project"]["type"] = "auto-detect"
        
        config_file = ai_dir / "config.json"
        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✓ 创建配置：.ai-dev-team/config.json")
    
    # 创建初始状态文件
    initial_state = {
        "v": 1,
        "tasks": {},
        "queue": [],
        "active": None,
        "initialized_at": datetime.now().isoformat()
    }
    state_file = ai_dir / "state.json"
    state_file.write_text(json.dumps(initial_state, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ 创建状态：.ai-dev-team/state.json")
    
    # 创建 README
    readme = ai_dir / "README.md"
    readme_content = f"""# AI Dev Team 项目

**项目名称:** {project_path.name}
**初始化时间:** {datetime.now().isoformat()}

## 目录结构

```
.ai-dev-team/
├── config.json    # 配置
├── state.json     # 状态机
├── tasks/         # 任务卡片
├── reports/       # 报告
├── docs/          # 文档缓存
└── logs/          # 日志
```

## 快速开始

```bash
# 分析项目
@ai-dev-team analyze

# 生成规划
@ai-dev-team plan

# 开始开发
@ai-dev-team start

# 查看状态
@ai-dev-team status
```

## 命令

| 命令 | 说明 |
|------|------|
| `init` | 初始化项目 |
| `analyze` | 分析项目 |
| `plan` | 生成规划 |
| `start` | 开始开发循环 |
| `status` | 查看状态 |
| `approve` | 验收任务 |
| `escalations` | 查看上报 |

---

*由 AI Dev Team 管理*
"""
    readme.write_text(readme_content, encoding="utf-8")
    print(f"  ✓ 创建说明：.ai-dev-team/README.md")
    
    print("\n✅ 项目初始化完成！")
    print(f"\n下一步：运行 `@ai-dev-team analyze` 分析项目")


def cmd_analyze(args):
    """分析项目"""
    print("🔍 分析项目...\n")
    
    agent = MainAgent(args.path)
    report = agent.analyze_project()
    
    print(f"\n📊 分析结果:")
    print(f"  技术栈：{', '.join([t['name'] for t in report['tech_stack']]) or '未识别'}")
    print(f"  文件数：{report['file_stats'].get('total_files', 0)}")
    print(f"  潜在任务：{len(report['potential_tasks'])}")
    
    if report['potential_tasks']:
        print("\n📋 识别的任务:")
        for i, task in enumerate(report['potential_tasks'][:5], 1):
            print(f"  {i}. {task['title']} ({task['priority']})")
    
    print(f"\n📄 详细报告：{report['report_file']}")
    print("\n下一步：运行 `@ai-dev-team plan` 生成详细规划")


def cmd_plan(args):
    """生成规划"""
    print("📝 生成开发规划...\n")
    
    agent = MainAgent(args.path)
    
    # 加载分析结果
    reports_dir = agent.ai_dir / "reports"
    analysis_reports = list(reports_dir.glob("project-analysis-*.md"))
    
    if not analysis_reports:
        print("⚠️  未找到项目分析报告，先运行 `@ai-dev-team analyze`")
        return
    
    # 读取最新分析报告
    latest_report = sorted(analysis_reports)[-1]
    print(f"📖 读取报告：{latest_report.name}")
    
    # 从状态文件加载已发现的任务
    pending_tasks = agent.state_manager.list_tasks(State.DISCOVERED)
    
    if not pending_tasks:
        # 自动创建任务
        print("\n📋 从分析报告创建任务...")
        # 这里简化处理，实际应该解析报告
        print("  （任务已在分析时自动创建）")
    
    # 生成规划报告
    plan_file = reports_dir / f"development-plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    
    plan_content = f"""# 开发规划

**生成时间:** {datetime.now().isoformat()}
**项目:** {agent.project_path.name}

---

## 任务队列

共 {len(pending_tasks)} 个待规划任务：

"""
    
    for i, task in enumerate(pending_tasks[:10], 1):
        plan_content += f"""
### {i}. {task.get('title', 'N/A')}

- **ID:** {task['tid']}
- **类型:** {task.get('type', 'feature')}
- **优先级:** {task.get('priority', 'normal')}
- **描述:** {task.get('description', 'N/A')}

**建议:**
- 先收集相关文档
- 实现核心功能
- 编写测试
- 代码审查

"""
    
    if len(pending_tasks) > 10:
        plan_content += f"\n*还有 {len(pending_tasks) - 10} 个任务未列出...*\n"
    
    plan_content += f"""
---

## 执行顺序建议

1. **高优先级任务** - 先处理基础设施和配置
2. **中优先级任务** - 核心功能开发
3. **低优先级任务** - 优化和文档

## 下一步

运行 `@ai-dev-team start` 开始开发循环

---

*规划由 AI Dev Team 主 Agent 生成*
"""
    
    plan_file.write_text(plan_content, encoding="utf-8")
    print(f"\n✅ 规划已生成：{plan_file}")
    
    # 将任务转移到待批准状态
    for task in pending_tasks:
        try:
            agent.state_manager.transition(task['tid'], State.PENDING_APPROVAL)
        except ValueError:
            pass  # 状态转换不合法则跳过
    
    print(f"\n📋 {len(pending_tasks)} 个任务已加入待批准队列")
    print("\n下一步：运行 `@ai-dev-team start` 开始开发")


def cmd_start(args):
    """开始开发循环"""
    print("🚀 开始开发循环...\n")
    
    agent = MainAgent(args.path)
    agent.run_development_cycle(auto_approve=args.auto_approve)


def cmd_status(args):
    """查看状态"""
    agent = MainAgent(args.path)
    stats = agent.status()
    
    print(f"📊 AI Dev Team 状态\n")
    print(f"  总任务数：{stats['total']}")
    print(f"  ✅ 已完成：{stats['completed']}")
    print(f"  🚧 进行中：{stats['active']}")
    print(f"  ⏳ 待批准：{stats['pending']}")
    print(f"  ⚠️  已上报：{stats['escalated']}")
    
    # 显示活跃任务
    active = agent.state_manager.get_active_task()
    if active:
        print(f"\n🔥 当前活跃任务:")
        print(f"  ID: {active['tid']}")
        print(f"  标题：{active.get('title', 'N/A')}")
        print(f"  Agent: {active.get('agent_id', 'N/A')}")
    
    # 显示待批准任务
    pending = agent.state_manager.list_tasks(State.PENDING_APPROVAL)
    if pending:
        print(f"\n⏳ 待批准任务 ({len(pending)}):")
        for task in pending[:5]:
            print(f"  - {task['tid']}: {task.get('title', 'N/A')}")


def cmd_approve(args):
    """验收任务"""
    agent = MainAgent(args.path)
    
    if not args.task_id:
        # 列出待验收任务
        pending = agent.state_manager.list_tasks(State.PENDING_HUMAN_TEST)
        
        if not pending:
            print("ℹ️  没有待验收的任务")
            return
        
        print("⏳ 待验收任务:\n")
        for task in pending:
            print(f"  ID: {task['tid']}")
            print(f"  标题：{task.get('title', 'N/A')}")
            print(f"  Agent: {task.get('agent_id', 'N/A')}")
            print()
        
        print("使用 `@ai-dev-team approve --task-id=<id> --approved=true/false` 进行验收")
        return
    
    # 验收指定任务
    approved = args.approved if args.approved is not None else True
    agent.human_test_approval(args.task_id, approved)


def cmd_escalations(args):
    """查看上报"""
    agent = MainAgent(args.path)
    
    escalated = agent.state_manager.list_tasks(State.ESCALATED)
    human_escalation = agent.state_manager.list_tasks(State.HUMAN_ESCALATION)
    
    print("⚠️  上报任务\n")
    
    if escalated:
        print(f"需要处理的上报 ({len(escalated)}):")
        for task in escalated:
            print(f"\n  ID: {task['tid']}")
            print(f"  标题：{task.get('title', 'N/A')}")
            print(f"  重试次数：{task.get('retry', 0)}")
            print(f"  Agent: {task.get('agent_id', 'N/A')}")
    else:
        print("  没有需要处理的上报")
    
    if human_escalation:
        print(f"\n等待人类决策 ({len(human_escalation)}):")
        for task in human_escalation:
            print(f"  - {task['tid']}: {task.get('title', 'N/A')}")


def cmd_research(args):
    """执行文档调研"""
    from researcher_agent import ResearcherAgent
    
    print("📚 执行文档调研...\n")
    
    agent = ResearcherAgent(args.path)
    
    if args.library and args.query:
        print(f"搜索：{args.library} - {args.query}")
        result = agent.get_context7_context(args.library, args.query)
        
        if result:
            print(f"\n{result['content']}")
        else:
            print("未找到相关文档")
    else:
        print("用法：@ai-dev-team research --library=<lib> --query=<query>")


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="AI Dev Team - 自主开发团队",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  @ai-dev-team init          # 初始化项目
  @ai-dev-team analyze       # 分析项目
  @ai-dev-team plan          # 生成规划
  @ai-dev-team start         # 开始开发
  @ai-dev-team status        # 查看状态
  @ai-dev-team approve       # 验收任务
        """
    )
    
    parser.add_argument("command", nargs="?", default="status",
                        choices=["init", "analyze", "plan", "start", "status", 
                                 "approve", "escalations", "research"],
                        help="命令")
    parser.add_argument("--path", default=".", help="项目路径")
    parser.add_argument("--auto-approve", action="store_true", help="自动批准任务")
    parser.add_argument("--task-id", help="任务 ID")
    parser.add_argument("--approved", type=lambda x: x.lower() == 'true', 
                        help="是否批准 (true/false)")
    parser.add_argument("--library", help="库名称（用于 research）")
    parser.add_argument("--query", help="查询内容（用于 research）")
    
    args = parser.parse_args()
    
    # 命令分发
    commands = {
        "init": cmd_init,
        "analyze": cmd_analyze,
        "plan": cmd_plan,
        "start": cmd_start,
        "status": cmd_status,
        "approve": cmd_approve,
        "escalations": cmd_escalations,
        "research": cmd_research
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
