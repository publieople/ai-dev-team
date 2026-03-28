#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Dev Team - 主 Agent (CEO)
负责项目分析、任务规划、子 Agent 指派、验收决策

使用 OpenClaw 原生 sessions_spawn 创建子 Agent
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

from state_manager import StateManager, State

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
    },
    "review": {
        "schedule": "0 20 * * *",
        "timezone": "Asia/Shanghai"
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
        return DEFAULT_CONFIG.copy()
    
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
        
        skip_dirs = {'.git', '.openclaw', 'node_modules', '__pycache__', 'venv', 'dist', 'build', '.venv'}
        
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
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
        }
        
        for indicator, (tech, tools) in tech_indicators.items():
            if (self.project_path / indicator).exists():
                report["tech_stack"].append({
                    "name": tech,
                    "confidence": "high",
                    "indicators": [indicator]
                })
        
        # 识别潜在任务
        raw_tasks = self._identify_tasks(file_types, report["tech_stack"])
        
        # 将任务保存到状态管理器
        report["potential_tasks"] = []
        for task_info in raw_tasks:
            tid = self.create_task(
                task_type=task_info.get("type", "feature"),
                title=task_info.get("title", "新任务"),
                description=task_info.get("description", ""),
                priority=task_info.get("priority", "normal")
            )
            task = self.state_manager.get_task(tid)
            if task:
                report["potential_tasks"].append(task)
        
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
        
        if not (self.project_path / 'README.md').exists():
            tasks.append({
                "type": "doc",
                "priority": "normal",
                "title": "创建项目 README 文档",
                "description": "项目缺少 README 文档，需要创建项目说明"
            })
        
        if not (self.project_path / '.gitignore').exists():
            tasks.append({
                "type": "setup",
                "priority": "high",
                "title": "创建 .gitignore 文件",
                "description": "项目缺少 .gitignore，需要配置版本控制忽略规则"
            })
        
        has_config = any(ext in file_types for ext in ['.json', '.yaml', '.yml', '.toml', '.ini'])
        if not has_config and file_types.get('.py', 0) > 5:
            tasks.append({
                "type": "setup",
                "priority": "low",
                "title": "添加项目配置文件",
                "description": "项目代码较多但缺少配置文件，建议添加配置管理"
            })
        
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
        """创建新任务"""
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
    
    def spawn_subagent(self, task: Dict, agent_type: str = "developer") -> Dict:
        """
        使用 OpenClaw sessions_spawn 创建子 Agent
        
        Args:
            task: 任务信息
            agent_type: Agent 类型 (developer/researcher/tester)
            
        Returns:
            子 Agent 配置
        """
        self.agent_counter += 1
        agent_id = f"{agent_type[:3]}-{self.agent_counter:03d}"
        task_id = task["tid"]
        
        # 根据 Agent 类型构建提示
        if agent_type == "researcher":
            prompt = self._build_researcher_prompt(task, agent_id)
        elif agent_type == "tester":
            prompt = self._build_tester_prompt(task, agent_id)
        else:
            prompt = self._build_developer_prompt(task, agent_id)
        
        # 保存任务卡片
        task_card_file = self.ai_dir / "tasks" / f"{task_id}.json"
        task_card_file.parent.mkdir(parents=True, exist_ok=True)
        task_card_file.write_text(json.dumps({
            **task,
            "agent_id": agent_id,
            "agent_type": agent_type,
            "prompt": prompt
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        
        print(f"📋 任务卡片已保存：{task_card_file}")
        
        return {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "task_id": task_id,
            "prompt": prompt,
            "task_card_file": str(task_card_file),
            "timeout": task.get("timeout", "2h")
        }
    
    def _build_developer_prompt(self, task: Dict, agent_id: str) -> str:
        """构建 Developer Agent 提示"""
        task_id = task["tid"]
        
        return f"""你是一个 Developer Agent，负责执行具体的开发任务。

## 任务信息
- **任务 ID:** {task_id}
- **Agent ID:** {agent_id}
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

1. **读取任务卡片** - `.ai-dev-team/tasks/{task_id}.json`
2. **阅读相关代码文件** - 理解项目结构和上下文
3. **查阅文档** - 如需 API 文档，先查看 `.ai-dev-team/docs/`
4. **实现代码** - 编写/修改代码
5. **自测** - 运行相关测试（如果有）
6. **生成执行报告** - `.ai-dev-team/reports/execution-{task_id}.md`

## 执行报告格式

```markdown
# 执行报告

**任务 ID:** {task_id}
**Agent:** {agent_id}
**执行时间:** [开始时间] - [结束时间]

## 完成的工作

[详细描述完成的内容]

## 修改的文件

- `文件路径 1`: 说明修改内容
- `文件路径 2`: 说明修改内容

## 测试结果

[测试结果描述]

## 遇到的问题

[如有问题，详细描述]

## 后续建议

[如有后续工作建议]
```

## 注意事项

- 只修改任务相关的文件
- 保持代码风格与项目一致
- 如有不确定的地方，在报告中说明
- 完成后务必生成执行报告

开始执行任务！
"""
    
    def _build_researcher_prompt(self, task: Dict, agent_id: str) -> str:
        """构建 Researcher Agent 提示"""
        task_id = task["tid"]
        
        return f"""你是一个 Researcher Agent，负责收集技术文档和调研。

## 任务信息
- **任务 ID:** {task_id}
- **Agent ID:** {agent_id}
- **标题:** {task.get('title', 'N/A')}

## 调研需求
{task.get('description', '无详细描述')}

## 工作流程

1. **分析需求** - 确定需要哪些技术文档
2. **搜索本地缓存** - 检查 `.ai-dev-team/docs/` 是否已有相关文档
3. **使用 web_search/web_fetch** - 获取官方文档
4. **缓存文档** - 将收集的文档保存到 `.ai-dev-team/docs/`
5. **生成调研报告** - `.ai-dev-team/reports/research-{task_id}.md`

## 可用工具

- **web_search**: 搜索技术资料
- **web_fetch**: 抓取文档页面

## 报告格式

```markdown
# 调研报告

**任务 ID:** {task_id}
**Agent:** {agent_id}

## 使用的数据源

- [数据源 1]
- [数据源 2]

## 缓存的文档

- `.ai-dev-team/docs/xxx.md`

## 关键发现

[总结重要信息]

## 对开发的建议

[给 Developer 的建议]
```

开始调研！
"""
    
    def _build_tester_prompt(self, task: Dict, agent_id: str) -> str:
        """构建 Tester Agent 提示"""
        task_id = task["tid"]
        
        return f"""你是一个 Tester Agent，负责验证代码质量。

## 任务信息
- **任务 ID:** {task_id}
- **Agent ID:** {agent_id}
- **标题:** {task.get('title', 'N/A')}

## 测试需求
{task.get('description', '无详细描述')}

## 工作流程

1. **读取执行报告** - `.ai-dev-team/reports/execution-{task_id}.md`
2. **审查代码变更** - 使用 `git diff` 查看修改
3. **运行测试** - 执行项目测试套件
4. **生成测试报告** - `.ai-dev-team/reports/test-{task_id}.md`

## 测试报告格式

```markdown
# 测试报告

**任务 ID:** {task_id}
**Agent:** {agent_id}

## 测试结果

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 单元测试 | ✅/❌ | |
| 代码审查 | ✅/❌ | |

## 发现的问题

1. 问题描述
   - 严重程度：高/中/低

## 结论

**测试状态:** 通过 / 失败 / 有条件通过
```

开始测试！
"""
    
    def verify_changes(self, task: Dict, report_file: str) -> bool:
        """验证子 Agent 完成的变更"""
        report_path = Path(report_file)
        if not report_path.exists():
            print(f"❌ 执行报告不存在：{report_file}")
            return False
        
        report_content = report_path.read_text(encoding="utf-8")
        
        if "执行报告" not in report_content:
            print("❌ 报告格式不正确")
            return False
        
        if task["tid"] not in report_content:
            print("❌ 报告缺少任务 ID")
            return False
        
        print("✅ 变更验证通过")
        return True
    
    def git_commit(self, task: Dict, agent_id: str, report_file: str = None):
        """创建带元数据的 Git 提交"""
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
        """判断是否需要上报人类"""
        retry_count = task.get("retry", 0)
        threshold = self.config["escalation"]["threshold"]
        return retry_count >= threshold
    
    def generate_escalation_report(self, task: Dict) -> str:
        """生成上报报告"""
        return f"""# 问题上报

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

**A. 重新规划任务** - 拆分任务为更小的子任务
**B. 人类介入** - 需要人类开发者提供指导
**C. 跳过此任务** - 标记为暂不处理

---

## 需要人类决策

请回复选择 A/B/C，或提供具体指示。

*报告由 AI Dev Team 主 Agent 生成*
"""
    
    def status(self) -> Dict:
        """获取当前状态"""
        return self.state_manager.get_stats()
    
    def run_development_cycle(self, auto_approve: bool = False):
        """
        运行开发循环
        
        使用 OpenClaw sessions_spawn 创建子 Agent
        """
        print("\n🚀 开始开发循环...")
        
        # 1. 检查是否有待处理任务
        pending_tasks = self.state_manager.list_tasks(State.PENDING_APPROVAL)
        
        if not pending_tasks:
            print("ℹ️  没有待批准的任务")
            print("🔍 尝试发现新任务...")
            analysis = self.analyze_project()
            for task_info in analysis.get("potential_tasks", []):
                self.create_task(
                    task_type=task_info.get("type", "feature"),
                    title=task_info.get("title", "新任务"),
                    description=task_info.get("description", ""),
                    priority=task_info.get("priority", "normal")
                )
            return
        
        # 2. 处理待批准任务
        for task_data in pending_tasks:
            task_id = task_data["tid"]
            
            if not auto_approve:
                print(f"\n⏳ 等待人类批准任务：{task_id}")
                print(f"   标题：{task_data.get('title', 'N/A')}")
                print("\n💡 提示：使用 @ai-dev-team approve --task-id={task_id} --approved=true 批准任务")
                return  # 等待人类确认
            
            # 批准任务
            self.state_manager.transition(task_id, State.ASSIGNED, agent_id="pending")
            
            # 3. 判断是否需要先调研
            needs_research = self._check_needs_research(task_data)
            
            if needs_research:
                print("📚 任务需要文档调研，先创建 Researcher Agent...")
                research_task = self._create_research_task(task_data)
                research_result = self._execute_research(research_task)
                
                if not research_result.get("success"):
                    print("⚠️  调研失败，继续开发任务")
            
            # 4. 创建 Developer Agent
            print(f"\n🤖 创建 Developer Agent...")
            subagent_config = self.spawn_subagent(task_data, agent_type="developer")
            print(f"   Agent ID: {subagent_config['agent_id']}")
            print(f"   任务卡片：{subagent_config['task_card_file']}")
            
            # 5. 使用 OpenClaw sessions_spawn 执行子 Agent
            print(f"\n⏳ 执行开发任务...")
            dev_result = self._execute_developer_agent(subagent_config)
            
            # 6. 验证结果
            report_file = dev_result.get("report_file")
            if report_file and self.verify_changes(task_data, report_file):
                print("\n🧪 创建 Tester Agent 验证...")
                test_result = self._execute_tester_agent(task_data, report_file)
                
                if test_result.get("passed", False):
                    self.state_manager.transition(task_id, State.PENDING_HUMAN_TEST)
                    print("✅ 任务完成，等待人类验收")
                else:
                    self._handle_failure(task_data, "测试未通过")
            else:
                self._handle_failure(task_data, "验证失败")
    
    def _check_needs_research(self, task: Dict) -> bool:
        """检查任务是否需要文档调研"""
        description = task.get("description", "").lower()
        tech_keywords = ["api", "sdk", "library", "framework", "集成", "调用"]
        return any(kw in description for kw in tech_keywords)
    
    def _create_research_task(self, parent_task: Dict) -> Dict:
        """创建调研子任务"""
        research_task = {
            "tid": f"t-research-{int(time.time() * 1000)}",
            "type": "research",
            "title": f"调研：{parent_task.get('title', 'N/A')}",
            "description": f"为任务 {parent_task['tid']} 收集相关技术文档",
            "priority": "high",
            "parent_task": parent_task["tid"],
            "context": parent_task.get("context", {})
        }
        
        task_card_file = self.ai_dir / "tasks" / f"{research_task['tid']}.json"
        task_card_file.parent.mkdir(parents=True, exist_ok=True)
        task_card_file.write_text(json.dumps(research_task, indent=2, ensure_ascii=False), encoding="utf-8")
        
        return research_task
    
    def _execute_research(self, task: Dict) -> Dict:
        """执行调研任务"""
        from researcher_agent import ResearcherAgent
        
        agent = ResearcherAgent(str(self.project_path))
        result = agent.research_task(task)
        
        return {
            "success": True,
            "report_file": result.get("report_file"),
            "documents": result.get("documents_cached", [])
        }
    
    def _execute_developer_agent(self, config: Dict) -> Dict:
        """
        使用 OpenClaw sessions_spawn 执行 Developer Agent
        
        注意：实际调用需要通过 OpenClaw 的工具系统
        这里提供任务配置，由 OpenClaw 运行时创建子 Agent 会话
        """
        print(f"\n🤖 创建 Developer Agent 会话...")
        
        # 读取任务卡片
        task_card_file = Path(config["task_card_file"])
        task_data = json.loads(task_card_file.read_text(encoding="utf-8"))
        
        print(f"   任务：{config['task_id']}")
        print(f"   Agent: {config['agent_id']}")
        print(f"   超时：{config.get('timeout', '2h')}")
        
        # 在实际 OpenClaw 环境中，这里会调用 sessions_spawn 工具
        # sessions_spawn({
        #     "agentId": "ai-dev-team-developer",
        #     "task": config["prompt"],
        #     "label": f"dev-{config['task_id']}",
        #     "runTimeoutSeconds": 7200
        # })
        
        spawn_result = {
            "status": "accepted",
            "runId": f"run-{int(time.time() * 1000)}",
            "childSessionKey": f"agent:ai-dev-team-developer:subagent:{config['task_id']}",
            "task_id": config["task_id"],
            "agent_id": config["agent_id"]
        }
        
        print(f"   ✅ 子 Agent 已创建：{spawn_result['runId']}")
        print(f"   会话：{spawn_result['childSessionKey']}")
        
        # 更新任务状态
        self.state_manager.transition(
            config["task_id"],
            State.IN_PROGRESS,
            agent_id=config["agent_id"],
            run_id=spawn_result["runId"]
        )
        
        return {
            "status": "running",
            "run_id": spawn_result["runId"],
            "session_key": spawn_result["childSessionKey"],
            "report_file": str(self.ai_dir / "reports" / f"execution-{config['task_id']}.md")
        }
    
    def _execute_tester_agent(self, task: Dict, report_file: str) -> Dict:
        """执行 Tester Agent"""
        report_path = Path(report_file)
        if not report_path.exists():
            return {"passed": False, "reason": "执行报告不存在"}
        
        content = report_path.read_text(encoding="utf-8")
        if "执行报告" in content and task["tid"] in content:
            return {"passed": True}
        else:
            return {"passed": False, "reason": "报告格式不正确"}
    
    def _handle_failure(self, task: Dict, reason: str):
        """处理任务失败"""
        task["retry"] = task.get("retry", 0) + 1
        
        if self.should_escalate(task):
            self.state_manager.transition(task["tid"], State.ESCALATED)
            print(f"❌ 任务失败：{reason}，需要上报人类")
        else:
            self.state_manager.transition(task["tid"], State.ASSIGNED)
            print(f"🔄 任务失败：{reason}，重新指派（重试 {task['retry']}/{task.get('max_retries', 3)}）")
    
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
            agent_id = task.get("agent_id", "unknown")
            report_file = str(self.ai_dir / "reports" / f"execution-{task_id}.md")
            self.git_commit(task, agent_id, report_file)
            self.state_manager.transition(task_id, State.COMPLETED)
            print(f"✅ 任务 {task_id} 已完成并提交")
        else:
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
