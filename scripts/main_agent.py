#!/usr/bin/env python3
"""
AI Dev Team - 主 Agent (CEO)
负责项目分析、任务规划、子 Agent 指派、验收决策
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# 导入状态管理
from state_manager import StateManager, State

# 默认配置
DEFAULT_CONFIG = {
    "workflow": {
        "auto_approve": False,
        "require_human_test": True,
        "max_concurrent_agents": 1,
        "default_timeout": "2h",
        "max_retries": 3
    },
    "escalation": {
        "threshold": 3,
        "consecutive_failures": 3
    },
    "git": {
        "auto_commit": True,
        "traceability": True
    }
}

class MainAgent:
    """主 Agent - CEO 角色"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.ai_dir = self.project_path / ".ai-dev-team"
        self.state_manager = StateManager(project_path)
        self.config = self._load_config()
        self.agent_counter = 0
        
    def _load_config(self) -> Dict:
        """加载配置"""
        config_file = self.ai_dir / "config.json"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return DEFAULT_CONFIG
    
    def _save_config(self, config: Dict):
        """保存配置"""
        config_file = self.ai_dir / "config.json"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def analyze_project(self) -> Dict:
        """
        分析项目结构，识别技术栈和优化点
        
        Returns:
            项目分析报告
        """
        print("\n🔍 开始项目分析...")
        
        report = {
            "name": self.project_path.name,
            "path": str(self.project_path),
            "analyzed_at": datetime.now().isoformat(),
            "tech_stack": [],
            "file_stats": {},
            "potential_tasks": []
        }
        
        # 扫描文件结构
        file_types = {}
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(self.project_path):
            # 跳过隐藏目录和常见忽略目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'dist', 'build']]
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                total_files += 1
                filepath = Path(root) / file
                try:
                    size = filepath.stat().st_size
                    total_size += size
                    ext = filepath.suffix.lower()
                    file_types[ext] = file_types.get(ext, 0) + 1
                except:
                    pass
        
        report["file_stats"] = {
            "total_files": total_files,
            "total_size_kb": round(total_size / 1024, 2),
            "by_extension": file_types
        }
        
        # 识别技术栈
        tech_indicators = {
            "package.json": ("JavaScript/Node.js", ["npm", "yarn", "node"]),
            "requirements.txt": ("Python", ["pip", "python"]),
            "Cargo.toml": ("Rust", ["cargo", "rust"]),
            "go.mod": ("Go", ["go"]),
            "pom.xml": ("Java/Maven", ["mvn", "java"]),
            "Gemfile": ("Ruby", ["bundle", "ruby"]),
            "composer.json": ("PHP", ["composer", "php"]),
            ".csproj": ("C#/.NET", ["dotnet", "msbuild"]),
            "CMakeLists.txt": ("C/C++", ["cmake", "make"]),
            "README.md": ("Documentation", []),
        }
        
        for indicator, (tech, tools) in tech_indicators.items():
            if (self.project_path / indicator).exists():
                report["tech_stack"].append({
                    "name": tech,
                    "confidence": "high",
                    "indicators": [indicator]
                })
        
        # 识别潜在任务
        report["potential_tasks"] = self._identify_tasks(file_types, report["tech_stack"])
        
        # 保存报告
        report_file = self.ai_dir / "reports" / f"project-analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        markdown = self._generate_analysis_report(report)
        report_file.write_text(markdown, encoding="utf-8")
        report["report_file"] = str(report_file)
        
        print(f"✅ 分析完成！报告：{report_file}")
        return report
    
    def _identify_tasks(self, file_types: Dict, tech_stack: List) -> List[Dict]:
        """识别潜在开发任务"""
        tasks = []
        
        # 根据文件类型推断任务
        if '.py' in file_types:
            if not (self.project_path / 'tests').exists():
                tasks.append({
                    "type": "test",
                    "priority": "high",
                    "title": "添加测试目录和基础测试框架",
                    "description": "项目包含 Python 代码但缺少测试目录，建议添加 pytest 或 unittest 框架"
                })
        
        if '.js' in file_types or '.ts' in file_types:
            if not (self.project_path / 'package.json').exists():
                tasks.append({
                    "type": "setup",
                    "priority": "normal",
                    "title": "初始化 Node.js 项目配置",
                    "description": "检测到 JS/TS 文件但缺少 package.json，建议初始化 npm 项目"
                })
        
        # 检查文档
        if not (self.project_path / 'README.md').exists():
            tasks.append({
                "type": "doc",
                "priority": "normal",
                "title": "创建项目 README 文档",
                "description": "项目缺少 README 文档，需要创建项目说明"
            })
        
        # 检查 Git 配置
        if not (self.project_path / '.gitignore').exists():
            tasks.append({
                "type": "setup",
                "priority": "high",
                "title": "创建 .gitignore 文件",
                "description": "项目缺少 .gitignore，需要配置版本控制忽略规则"
            })
        
        # 检查配置文件
        has_config = any(ext in file_types for ext in ['.json', '.yaml', '.yml', '.toml', '.ini'])
        if not has_config and file_types.get('.py', 0) > 5:
            tasks.append({
                "type": "setup",
                "priority": "low",
                "title": "添加项目配置文件",
                "description": "项目代码较多但缺少配置文件，建议添加配置管理"
            })
        
        # 为每个任务生成 ID
        for i, task in enumerate(tasks):
            task["tid"] = f"t-discover-{int(time.time())}-{i}"
            task["state"] = "DISCOVERED"
            task["created_at"] = datetime.now().isoformat()
        
        return tasks
    
    def _generate_analysis_report(self, report: Dict) -> str:
        """生成分析报告 Markdown"""
        md = f"""# 项目分析报告

**项目名称:** {report['name']}
**分析时间:** {report['analyzed_at']}
**路径:** {report['path']}

---

## 技术栈识别

"""
        if report['tech_stack']:
            for tech in report['tech_stack']:
                md += f"- {tech['name']} (可信度：{tech['confidence']})\n"
        else:
            md += "未识别到明确的技术栈\n"
        
        md += f"""
---

## 文件统计

- **总文件数:** {report['file_stats'].get('total_files', 0)}
- **总大小:** {report['file_stats'].get('total_size_kb', 0)} KB

### 按扩展名分布

"""
        by_ext = report['file_stats'].get('by_extension', {})
        sorted_ext = sorted(by_ext.items(), key=lambda x: x[1], reverse=True)[:10]
        for ext, count in sorted_ext:
            md += f"- `{ext}`: {count} 文件\n"
        
        md += f"""
---

## 潜在开发任务

共识别 **{len(report['potential_tasks'])}** 个潜在任务：

"""
        for i, task in enumerate(report['potential_tasks'], 1):
            md += f"""
### {i}. {task['title']}

- **类型:** {task['type']}
- **优先级:** {task['priority']}
- **描述:** {task['description']}

"""
        
        md += """
---

## 下一步

1. 审阅以上识别的任务
2. 运行 `@ai-dev-team plan` 生成详细开发规划
3. 确认后开始开发循环

*报告由 AI Dev Team 主 Agent 生成*
"""
        return md
    
    def create_task(self, task_type: str, title: str, description: str, 
                    priority: str = "normal", files: List[str] = None,
                    constraints: List[str] = None) -> str:
        """
        创建新任务
        
        Returns:
            任务 ID
        """
        task = {
            "tid": f"t-{int(time.time() * 1000)}",
            "type": task_type,
            "title": title,
            "description": description,
            "priority": priority,
            "context": {
                "files": files or [],
                "constraints": constraints or []
            },
            "deliverables": ["代码实现", "执行报告"],
            "max_retries": self.config["workflow"]["max_retries"],
            "timeout": self.config["workflow"]["default_timeout"]
        }
        
        tid = self.state_manager.create_task(task)
        print(f"✅ 创建任务：{tid}")
        return tid
    
    def spawn_subagent(self, task: Dict) -> Dict:
        """
        创建子 Agent 执行任务
        
        使用 OpenClaw sessions_spawn 创建隔离会话
        """
        self.agent_counter += 1
        agent_id = f"dev-{self.agent_counter:03d}"
        
        task_id = task["tid"]
        
        # 构建任务提示
        prompt = f"""你是一个 Developer Agent，负责执行具体的开发任务。

## 任务信息
- **任务 ID:** {task_id}
- **类型:** {task.get('type', 'feature')}
- **标题:** {task.get('title', 'N/A')}
- **优先级:** {task.get('priority', 'normal')}

## 任务描述
{task.get('description', '无详细描述')}

## 相关文件
{', '.join(task.get('context', {}).get('files', [])) or '无特定文件'}

## 约束条件
{chr(10).join(task.get('context', {}).get('constraints', [])) or '无特殊约束'}

## 你的工作流程

1. **读取上下文** - 阅读相关代码文件，理解项目结构
2. **理解任务** - 明确需要实现的功能
3. **实现代码** - 编写/修改代码
4. **自测** - 运行相关测试（如果有）
5. **生成报告** - 写入执行报告到 `.ai-dev-team/reports/execution-{task_id}.md`

## 执行报告格式

```markdown
# 执行报告

**任务 ID:** {task_id}
**Agent:** {agent_id}
**执行时间:** {{开始时间}} - {{结束时间}}

## 完成的工作

{{详细描述完成的内容}}

## 修改的文件

- `文件路径 1`: 说明修改内容
- `文件路径 2`: 说明修改内容

## 测试结果

{{测试结果描述}}

## 遇到的问题

{{如有问题，详细描述}}

## 后续建议

{{如有后续工作建议}}
```

## 注意事项

- 只修改任务相关的文件
- 保持代码风格与项目一致
- 如有不确定的地方，在报告中说明
- 完成后务必生成执行报告

开始执行任务！
"""
        
        # 保存任务卡片
        task_card_file = self.ai_dir / "tasks" / f"{task_id}.json"
        task_card_file.parent.mkdir(parents=True, exist_ok=True)
        with open(task_card_file, "w", encoding="utf-8") as f:
            json.dump({
                **task,
                "agent_id": agent_id,
                "prompt": prompt
            }, f, indent=2, ensure_ascii=False)
        
        print(f"📋 任务卡片已保存：{task_card_file}")
        
        # 返回子 Agent 配置（由 OpenClaw 调用）
        return {
            "agent_id": agent_id,
            "task_id": task_id,
            "prompt": prompt,
            "task_card_file": str(task_card_file),
            "timeout": task.get("timeout", "2h")
        }
    
    def verify_changes(self, task: Dict, report_file: str) -> bool:
        """
        验证子 Agent 完成的变更
        
        Returns:
            是否通过验证
        """
        report_path = Path(report_file)
        if not report_path.exists():
            print(f"❌ 执行报告不存在：{report_file}")
            return False
        
        # 读取报告
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        
        # 基本验证
        if "执行报告" not in report_content:
            print("❌ 报告格式不正确")
            return False
        
        if task["tid"] not in report_content:
            print("❌ 报告缺少任务 ID")
            return False
        
        # 检查修改的文件是否存在
        # (实际实现中可以检查 git diff)
        
        print("✅ 变更验证通过")
        return True
    
    def git_commit(self, task: Dict, agent_id: str, report_file: str = None):
        """
        创建带元数据的 Git 提交
        """
        from git_wrapper import create_commit
        
        commit_type_map = {
            "feature": "feat",
            "bugfix": "fix",
            "refactor": "refactor",
            "test": "test",
            "doc": "docs",
            "setup": "chore"
        }
        
        commit_type = commit_type_map.get(task.get("type", "feature"), "feat")
        
        result = create_commit(
            message=task.get("title", "AI 开发任务"),
            task_id=task["tid"],
            agent_id=agent_id,
            report_file=report_file,
            commit_type=commit_type,
            cwd=str(self.project_path)
        )
        
        print(f"✅ Git 提交：{result['hash'][:8]} - {result['message']}")
        return result
    
    def should_escalate(self, task: Dict) -> bool:
        """
        判断是否需要上报人类
        """
        retry_count = task.get("retry", 0)
        threshold = self.config["escalation"]["threshold"]
        
        if retry_count >= threshold:
            return True
        
        return False
    
    def generate_escalation_report(self, task: Dict) -> str:
        """生成上报报告"""
        report = f"""# 问题上报

**任务 ID:** {task['tid']}
**任务类型:** {task.get('type', 'unknown')}
**任务标题:** {task.get('title', 'N/A')}
**重试次数:** {task.get('retry', 0)}
**上报时间:** {datetime.now().isoformat()}

---

## 问题描述

子 Agent 多次尝试执行任务失败。

## 已尝试的方案

1. 指派子 Agent 执行
2. 重试 {task.get('retry', 0)} 次

## 建议选项

**A. 重新规划任务**
- 拆分任务为更小的子任务
- 调整实现方案

**B. 人类介入**
- 需要人类开发者提供指导
- 可能需要手动实现部分代码

**C. 跳过此任务**
- 标记为暂不处理
- 记录技术债务

---

## 需要人类决策

请回复选择 A/B/C，或提供具体指示。

*报告由 AI Dev Team 主 Agent 生成*
"""
        return report
    
    def status(self) -> Dict:
        """获取当前状态"""
        return self.state_manager.get_stats()
    
    def run_development_cycle(self, auto_approve: bool = False):
        """
        运行开发循环
        
        Args:
            auto_approve: 是否自动批准任务（跳过人类确认）
        """
        print("\n🚀 开始开发循环...")
        
        # 1. 检查是否有待处理任务
        pending_tasks = self.state_manager.list_tasks(State.PENDING_APPROVAL)
        
        if not pending_tasks:
            print("ℹ️  没有待批准的任务")
            # 可以尝试发现新任务
            print("🔍 尝试发现新任务...")
            # 这里可以调用 analyze_project 并自动创建任务
        
        # 2. 处理待批准任务
        for task_data in pending_tasks:
            task_id = task_data["tid"]
            
            if not auto_approve:
                print(f"\n⏳ 等待人类批准任务：{task_id}")
                print(f"   标题：{task_data.get('title', 'N/A')}")
                # 实际实现中需要等待人类输入
                approval = input("批准此任务？(y/n): ").strip().lower()
                if approval != 'y':
                    self.state_manager.transition(task_id, State.CANCELLED)
                    continue
            
            # 批准任务
            self.state_manager.transition(task_id, State.ASSIGNED)
            
            # 3. 创建子 Agent
            subagent_config = self.spawn_subagent(task_data)
            print(f"🤖 创建子 Agent: {subagent_config['agent_id']}")
            
            # 4. 等待子 Agent 完成（实际实现中用 sessions_spawn）
            # 这里简化处理
            print(f"⏳ 等待子 Agent 执行...")
            
            # 5. 验证结果
            report_file = str(self.ai_dir / "reports" / f"execution-{task_id}.md")
            if self.verify_changes(task_data, report_file):
                self.state_manager.transition(task_id, State.PENDING_HUMAN_TEST)
                print("✅ 任务完成，等待人类验收")
            else:
                task_data["retry"] = task_data.get("retry", 0) + 1
                if self.should_escalate(task_data):
                    self.state_manager.transition(task_id, State.ESCALATED)
                    print("❌ 任务失败，需要上报人类")
                else:
                    self.state_manager.transition(task_id, State.ASSIGNED)
                    print("🔄 任务失败，重新指派")
    
    def human_test_approval(self, task_id: str, approved: bool):
        """
        人类验收
        
        Args:
            task_id: 任务 ID
            approved: 是否批准
        """
        task = self.state_manager.get_task(task_id)
        if not task:
            print(f"❌ 任务不存在：{task_id}")
            return
        
        if approved:
            # Git 提交
            agent_id = task.get("agent_id", "unknown")
            report_file = str(self.ai_dir / "reports" / f"execution-{task_id}.md")
            self.git_commit(task, agent_id, report_file)
            
            # 标记完成
            self.state_manager.transition(task_id, State.COMPLETED)
            print(f"✅ 任务 {task_id} 已完成并提交")
        else:
            # 返回重新分析
            self.state_manager.transition(task_id, State.ANALYZING)
            print(f"🔄 任务 {task_id} 未通过验收，返回重新分析")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Dev Team 主 Agent")
    parser.add_argument("command", choices=["analyze", "create-task", "status", "run", "approve"],
                        help="命令")
    parser.add_argument("--path", default=".", help="项目路径")
    parser.add_argument("--auto-approve", action="store_true", help="自动批准任务")
    parser.add_argument("--task-id", help="任务 ID（用于 approve 命令）")
    parser.add_argument("--approved", type=bool, default=True, help="是否批准（用于 approve 命令）")
    
    args = parser.parse_args()
    
    agent = MainAgent(args.path)
    
    if args.command == "analyze":
        report = agent.analyze_project()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    elif args.command == "create-task":
        # 从 stdin 读取任务信息
        task_info = json.load(sys.stdin)
        tid = agent.create_task(
            task_type=task_info.get("type", "feature"),
            title=task_info.get("title", "新任务"),
            description=task_info.get("description", ""),
            priority=task_info.get("priority", "normal"),
            files=task_info.get("files", []),
            constraints=task_info.get("constraints", [])
        )
        print(f"创建任务：{tid}")
    
    elif args.command == "status":
        stats = agent.status()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.command == "run":
        agent.run_development_cycle(auto_approve=args.auto_approve)
    
    elif args.command == "approve":
        if not args.task_id:
            print("❌ 需要指定 --task-id")
            sys.exit(1)
        agent.human_test_approval(args.task_id, args.approved)


if __name__ == "__main__":
    main()
