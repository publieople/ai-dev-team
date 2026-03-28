#!/usr/bin/env python3
"""
AI Dev Team - Developer Agent
负责执行具体的编码任务
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class DeveloperAgent:
    """开发工程师 Agent"""
    
    def __init__(self, project_path: str = ".", task_id: str = None):
        self.project_path = Path(project_path).resolve()
        self.ai_dir = self.project_path / ".ai-dev-team"
        self.task_id = task_id
        self.task = None
        self.changes = []
        self.start_time = None
        self.agent_id = f"dev-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
    def load_task(self, task_id: str = None):
        """加载任务卡片"""
        task_id = task_id or self.task_id
        if not task_id:
            raise ValueError("未指定任务 ID")
        
        task_file = self.ai_dir / "tasks" / f"{task_id}.json"
        if not task_file.exists():
            raise FileNotFoundError(f"任务卡片不存在：{task_file}")
        
        with open(task_file, "r", encoding="utf-8") as f:
            self.task = json.load(f)
        
        self.task_id = task_id
        print(f"📋 加载任务：{self.task.get('title', 'N/A')}")
        return self.task
    
    def read_context(self, files: List[str]) -> Dict[str, str]:
        """
        读取相关文件的上下文
        
        Returns:
            {文件路径：文件内容}
        """
        context = {}
        
        for filepath in files:
            full_path = self.project_path / filepath
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8")
                    context[filepath] = content
                    print(f"  ✓ 读取：{filepath} ({len(content)} 字符)")
                except Exception as e:
                    print(f"  ⚠️ 无法读取 {filepath}: {e}")
            else:
                print(f"  ⚠️ 文件不存在：{filepath}")
        
        return context
    
    def analyze_code(self, code: str, filepath: str) -> Dict:
        """
        分析代码结构（简化版）
        
        Returns:
            分析结果
        """
        result = {
            "filepath": filepath,
            "lines": len(code.split("\n")),
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        # 简单模式匹配（可以改进为使用 AST）
        for i, line in enumerate(code.split("\n"), 1):
            line = line.strip()
            
            # 检测函数定义
            if line.startswith("def ") or line.startswith("function ") or line.startswith("const ") and "=>" in line:
                result["functions"].append({"line": i, "code": line[:80]})
            
            # 检测类定义
            if line.startswith("class "):
                result["classes"].append({"line": i, "code": line[:80]})
            
            # 检测导入
            if line.startswith("import ") or line.startswith("from "):
                result["imports"].append(line[:80])
        
        return result
    
    def implement_task(self) -> Dict:
        """
        实现任务
        
        这是核心方法，实际开发逻辑由 AI 决定
        这里提供框架和工具
        
        Returns:
            实现结果
        """
        if not self.task:
            raise ValueError("未加载任务")
        
        self.start_time = datetime.now()
        print(f"\n🚀 开始实现任务：{self.task['tid']}")
        
        result = {
            "task_id": self.task["tid"],
            "agent_id": self.agent_id,
            "start_time": self.start_time.isoformat(),
            "files_modified": [],
            "files_created": [],
            "tests_run": [],
            "issues": []
        }
        
        # 1. 读取相关上下文
        context_files = self.task.get("context", {}).get("files", [])
        if context_files:
            print("\n📖 读取代码上下文...")
            context = self.read_context(context_files)
        
        # 2. 分析现有代码
        for filepath, content in context.items():
            analysis = self.analyze_code(content, filepath)
            print(f"  分析：{filepath} - {analysis['lines']} 行，{len(analysis['functions'])} 个函数")
        
        # 3. 实现逻辑（由 AI 决定具体内容）
        # 这里提供工具和框架，具体实现由 AI 填充
        print("\n💻 开始编码...")
        
        # 示例：创建或修改文件
        # 实际使用时，AI 应该根据任务需求决定修改哪些文件
        
        # 4. 运行测试（如果有）
        print("\n🧪 运行测试...")
        test_result = self.run_tests()
        result["tests_run"] = test_result
        
        # 5. 记录变更
        result["end_time"] = datetime.now().isoformat()
        result["duration_seconds"] = (datetime.now() - self.start_time).total_seconds()
        
        return result
    
    def modify_file(self, filepath: str, new_content: str, reason: str = "") -> bool:
        """
        修改文件
        
        Args:
            filepath: 文件路径（相对于项目根目录）
            new_content: 新内容
            reason: 修改原因
            
        Returns:
            是否成功
        """
        full_path = self.project_path / filepath
        
        # 备份原文件（如果存在）
        if full_path.exists():
            backup_path = full_path.with_suffix(full_path.suffix + ".bak")
            backup_path.write_text(full_path.read_text(encoding="utf-8"), encoding="utf-8")
            print(f"  💾 备份：{filepath} → {backup_path.name}")
        
        # 创建父目录
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入新内容
        full_path.write_text(new_content, encoding="utf-8")
        
        self.changes.append({
            "type": "modify" if full_path.exists() else "create",
            "filepath": filepath,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"  ✓ 写入：{filepath}")
        return True
    
    def run_tests(self) -> List[Dict]:
        """
        运行测试
        
        Returns:
            测试结果列表
        """
        results = []
        
        # 检测测试框架
        test_dirs = ["tests", "test", "__tests__", "spec"]
        
        for test_dir in test_dirs:
            test_path = self.project_path / test_dir
            if test_path.exists():
                print(f"  发现测试目录：{test_dir}")
                
                # 尝试运行 pytest
                if (self.project_path / "pytest.ini").exists() or \
                   (self.project_path / "pyproject.toml").exists():
                    result = self._run_pytest()
                    if result:
                        results.append(result)
                
                # 尝试运行 npm test
                if (self.project_path / "package.json").exists():
                    result = self._run_npm_test()
                    if result:
                        results.append(result)
        
        # 如果没有找到测试，返回空结果
        if not results:
            results.append({
                "type": "none",
                "status": "skipped",
                "message": "未找到测试配置"
            })
        
        return results
    
    def _run_pytest(self) -> Optional[Dict]:
        """运行 pytest"""
        try:
            result = subprocess.run(
                ["pytest", "--tb=short"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "type": "pytest",
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout,
                "error": result.stderr[-500:] if len(result.stderr) > 500 else result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "type": "pytest",
                "status": "timeout",
                "message": "测试超时（>5 分钟）"
            }
        except FileNotFoundError:
            return None
    
    def _run_npm_test(self) -> Optional[Dict]:
        """运行 npm test"""
        try:
            result = subprocess.run(
                ["npm", "test"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "type": "npm test",
                "status": "passed" if result.returncode == 0 else "failed",
                "output": result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout,
                "error": result.stderr[-500:] if len(result.stderr) > 500 else result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "type": "npm test",
                "status": "timeout",
                "message": "测试超时（>5 分钟）"
            }
        except FileNotFoundError:
            return None
    
    def generate_execution_report(self, result: Dict) -> str:
        """
        生成执行报告
        
        Returns:
            报告文件路径
        """
        report_file = self.ai_dir / "reports" / f"execution-{self.task_id}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        report_md = f"""# 执行报告

**任务 ID:** {self.task_id}
**Agent:** {self.agent_id}
**执行时间:** {result.get('start_time', 'N/A')} - {result.get('end_time', 'N/A')}
**耗时:** {result.get('duration_seconds', 0):.1f} 秒

---

## 完成的工作

{self.task.get('description', '无详细描述')}

## 修改的文件

"""
        for change in self.changes:
            report_md += f"- `{change['filepath']}`: {change['reason'] or '代码实现'}\n"
        
        if not self.changes:
            report_md += "*无文件修改*\n"
        
        report_md += f"""
## 测试结果

"""
        for test in result.get('tests_run', []):
            status_icon = "✅" if test.get('status') == 'passed' else "❌"
            report_md += f"- {test.get('type', 'unknown')}: {status_icon} {test.get('status', 'unknown')}\n"
            if test.get('message'):
                report_md += f"  > {test['message']}\n"
        
        report_md += f"""
## 遇到的问题

"""
        issues = result.get('issues', [])
        if issues:
            for issue in issues:
                report_md += f"- {issue}\n"
        else:
            report_md += "*无*\n"
        
        report_md += f"""
## 后续建议

*根据任务完成情况填写*

---

*报告由 AI Dev Team Developer Agent 生成*
"""
        report_file.write_text(report_md, encoding="utf-8")
        print(f"📄 执行报告已保存：{report_file}")
        return str(report_file)
    
    def execute(self) -> Dict:
        """
        完整执行流程
        
        Returns:
            执行结果
        """
        # 加载任务
        self.load_task()
        
        # 实现任务
        result = self.implement_task()
        
        # 生成报告
        report_file = self.generate_execution_report(result)
        result["report_file"] = report_file
        
        return result


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Developer Agent")
    parser.add_argument("--path", default=".", help="项目路径")
    parser.add_argument("--task-id", required=True, help="任务 ID")
    parser.add_argument("--action", choices=["execute", "read-context", "test"],
                        default="execute", help="操作类型")
    
    args = parser.parse_args()
    
    agent = DeveloperAgent(args.path, args.task_id)
    
    if args.action == "execute":
        result = agent.execute()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "read-context":
        agent.load_task()
        files = agent.task.get('context', {}).get('files', [])
        context = agent.read_context(files)
        for filepath, content in context.items():
            print(f"\n=== {filepath} ===")
            print(content[:500] + "..." if len(content) > 500 else content)
    
    elif args.action == "test":
        agent.load_task()
        results = agent.run_tests()
        print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
