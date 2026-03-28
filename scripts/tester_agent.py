#!/usr/bin/env python3
"""
AI Dev Team - Tester Agent
负责验证代码质量和功能正确性
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class TesterAgent:
    """测试工程师 Agent"""
    
    def __init__(self, project_path: str = ".", task_id: str = None):
        self.project_path = Path(project_path).resolve()
        self.ai_dir = self.project_path / ".ai-dev-team"
        self.task_id = task_id
        self.task = None
        self.agent_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
    def load_task(self, task_id: str = None):
        """加载任务"""
        task_id = task_id or self.task_id
        if not task_id:
            raise ValueError("未指定任务 ID")
        
        task_file = self.ai_dir / "tasks" / f"{task_id}.json"
        if not task_file.exists():
            raise FileNotFoundError(f"任务卡片不存在：{task_file}")
        
        with open(task_file, "r", encoding="utf-8") as f:
            self.task = json.load(f)
        
        self.task_id = task_id
        print(f"📋 加载测试任务：{self.task.get('title', 'N/A')}")
        return self.task
    
    def review_code_changes(self, task_id: str) -> Dict:
        """
        审查代码变更
        
        使用 git diff 查看修改
        """
        print("\n🔍 审查代码变更...")
        
        result = {
            "files_changed": [],
            "lines_added": 0,
            "lines_deleted": 0,
            "has_sensitive_changes": False,
            "issues": []
        }
        
        try:
            # 查找该任务的 Git 提交
            from git_wrapper import find_ai_commits
            commits = find_ai_commits(task_id, cwd=str(self.project_path))
            
            if not commits:
                # 没有提交，查看工作区变更
                diff_result = subprocess.run(
                    ["git", "diff", "--stat"],
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True
                )
                
                if diff_result.stdout:
                    result["files_changed"] = diff_result.stdout.strip().split("\n")
                    result["issues"].append("变更未提交")
                else:
                    result["issues"].append("未发现代码变更")
            else:
                # 查看最新提交的变更
                latest_commit = commits[0]["hash"]
                diff_result = subprocess.run(
                    ["git", "show", "--stat", latest_commit],
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True
                )
                
                if diff_result.stdout:
                    lines = diff_result.stdout.strip().split("\n")
                    for line in lines:
                        if "|" in line and "changed" in line:
                            # 解析统计信息
                            parts = line.split(",")
                            result["files_changed"] = [p.strip() for p in parts if p.strip()]
                
                # 获取详细 diff
                diff_detail = subprocess.run(
                    ["git", "show", latest_commit, "--no-stat"],
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True
                )
                
                # 统计行数
                for line in diff_detail.stdout.split("\n"):
                    if line.startswith("+") and not line.startswith("+++"):
                        result["lines_added"] += 1
                    elif line.startswith("-") and not line.startswith("---"):
                        result["lines_deleted"] += 1
                
                # 检查敏感变更
                sensitive_patterns = ["password", "secret", "api_key", "token", "credential"]
                for line in diff_detail.stdout.split("\n"):
                    if any(p in line.lower() for p in sensitive_patterns):
                        result["has_sensitive_changes"] = True
                        result["issues"].append(f"⚠️  发现敏感信息：{line.strip()[:50]}")
            
            print(f"  文件变更：{len(result['files_changed'])}")
            print(f"  新增行数：{result['lines_added']}")
            print(f"  删除行数：{result['lines_deleted']}")
            
        except Exception as e:
            result["issues"].append(f"审查失败：{e}")
            print(f"  ⚠️  审查失败：{e}")
        
        return result
    
    def run_tests(self) -> Dict:
        """
        运行测试套件
        
        Returns:
            测试结果
        """
        print("\n🧪 运行测试...")
        
        result = {
            "framework": None,
            "status": "skipped",
            "passed": 0,
            "failed": 0,
            "output": "",
            "issues": []
        }
        
        # 检测测试框架
        test_frameworks = [
            ("pytest", ["pytest", "--version"], ["pytest"]),
            ("npm test", ["npm", "test"], ["npm"]),
            ("jest", ["npx", "jest", "--version"], ["npx"]),
            ("unittest", ["python", "-m", "unittest", "--help"], ["python"]),
        ]
        
        for framework, test_cmd, check_bins in test_frameworks:
            # 检查是否有配置文件
            config_files = {
                "pytest": ["pytest.ini", "pyproject.toml", "setup.cfg"],
                "npm test": ["package.json"],
                "jest": ["jest.config.js", "jest.config.json"],
                "unittest": []
            }
            
            has_config = any((self.project_path / f).exists() for f in config_files.get(framework, []))
            
            if has_config or framework == "unittest":
                print(f"  发现测试框架：{framework}")
                result["framework"] = framework
                
                try:
                    test_result = subprocess.run(
                        test_cmd,
                        cwd=str(self.project_path),
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    result["output"] = test_result.stdout[-2000:] if len(test_result.stdout) > 2000 else test_result.stdout
                    
                    if test_result.returncode == 0:
                        result["status"] = "passed"
                        result["passed"] = 1
                        print(f"  ✅ 测试通过")
                    else:
                        result["status"] = "failed"
                        result["failed"] = 1
                        result["issues"].append(f"测试失败：{test_result.stderr[:500]}")
                        print(f"  ❌ 测试失败")
                    
                    return result
                    
                except subprocess.TimeoutExpired:
                    result["status"] = "timeout"
                    result["issues"].append("测试超时（>5 分钟）")
                    print(f"  ⏱️  测试超时")
                    return result
                except FileNotFoundError:
                    continue
        
        result["status"] = "no_tests"
        result["issues"].append("未找到测试配置")
        print(f"  ℹ️  未找到测试配置")
        return result
    
    def check_execution_report(self, report_file: str) -> Dict:
        """
        检查执行报告
        
        Returns:
            检查结果
        """
        print("\n📄 检查执行报告...")
        
        result = {
            "exists": False,
            "valid": False,
            "completeness": 0,
            "issues": []
        }
        
        report_path = Path(report_file)
        if not report_path.exists():
            result["issues"].append("执行报告不存在")
            print(f"  ❌ 报告不存在：{report_file}")
            return result
        
        result["exists"] = True
        content = report_path.read_text(encoding="utf-8")
        
        # 检查必需元素
        required_elements = [
            ("任务 ID", self.task_id),
            ("执行报告", "执行报告"),
            ("完成的工作", "完成的工作"),
            ("修改的文件", "修改的文件"),
        ]
        
        found = 0
        for name, keyword in required_elements:
            if keyword in content:
                found += 1
                print(f"  ✓ {name}")
            else:
                result["issues"].append(f"缺少：{name}")
                print(f"  ✗ 缺少：{name}")
        
        result["completeness"] = found / len(required_elements)
        result["valid"] = result["completeness"] >= 0.75
        
        if result["valid"]:
            print(f"  ✅ 报告有效（完整度：{result['completeness']*100:.0f}%）")
        else:
            print(f"  ⚠️  报告不完整（完整度：{result['completeness']*100:.0f}%）")
        
        return result
    
    def generate_test_report(self, results: Dict) -> str:
        """
        生成测试报告
        
        Returns:
            报告文件路径
        """
        report_file = self.ai_dir / "reports" / f"test-{self.task_id}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 确定总体状态
        overall_passed = (
            results.get("code_review", {}).get("valid", True) and
            results.get("tests", {}).get("status") != "failed" and
            results.get("report_check", {}).get("valid", False)
        )
        
        status_icon = "✅" if overall_passed else "❌"
        
        report_md = f"""# 测试报告

**任务 ID:** {self.task_id}
**测试 Agent:** {self.agent_id}
**测试时间:** {datetime.now().isoformat()}

---

## 测试结果汇总

**总体状态:** {status_icon} {"通过" if overall_passed else "失败"}

---

## 代码审查

"""
        code_review = results.get("code_review", {})
        if code_review:
            report_md += f"""
- **文件变更:** {len(code_review.get('files_changed', []))}
- **新增行数:** {code_review.get('lines_added', 0)}
- **删除行数:** {code_review.get('lines_deleted', 0)}
- **敏感信息:** {"⚠️  发现" if code_review.get('has_sensitive_changes') else "✅ 无"}

"""
            for issue in code_review.get("issues", []):
                report_md += f"- {issue}\n"
        else:
            report_md += "*未执行代码审查*\n"
        
        report_md += f"""
---

## 测试执行

"""
        tests = results.get("tests", {})
        if tests:
            test_status = tests.get("status", "unknown")
            status_icon = "✅" if test_status == "passed" else "❌" if test_status == "failed" else "⚠️"
            
            report_md += f"""
- **框架:** {tests.get('framework', 'unknown')}
- **状态:** {status_icon} {test_status}
- **通过:** {tests.get('passed', 0)}
- **失败:** {tests.get('failed', 0)}

"""
            if tests.get("output"):
                report_md += f"### 测试输出\n\n```\n{tests['output'][:1000]}\n```\n\n"
            
            for issue in tests.get("issues", []):
                report_md += f"- {issue}\n"
        else:
            report_md += "*未执行测试*\n"
        
        report_md += f"""
---

## 执行报告检查

"""
        report_check = results.get("report_check", {})
        if report_check:
            completeness = report_check.get("completeness", 0) * 100
            status_icon = "✅" if report_check.get("valid") else "❌"
            
            report_md += f"""
- **报告存在:** {"✅" if report_check.get('exists') else "❌"}
- **报告有效:** {status_icon}
- **完整度:** {completeness:.0f}%

"""
            for issue in report_check.get("issues", []):
                report_md += f"- {issue}\n"
        else:
            report_md += "*未检查*\n"
        
        report_md += f"""
---

## 结论

**测试状态:** {"✅ 通过" if overall_passed else "❌ 失败"}

**建议:** {"可以提交" if overall_passed else "需要修复后重新测试"}

---

*报告由 AI Dev Team Tester Agent 生成*
"""
        
        report_file.write_text(report_md, encoding="utf-8")
        print(f"\n📄 测试报告已保存：{report_file}")
        return str(report_file)
    
    def execute(self) -> Dict:
        """
        完整执行流程
        
        Returns:
            测试结果
        """
        # 加载任务
        self.load_task()
        
        results = {}
        
        # 1. 检查执行报告
        report_file = str(self.ai_dir / "reports" / f"execution-{self.task_id}.md")
        results["report_check"] = self.check_execution_report(report_file)
        
        # 2. 审查代码变更
        results["code_review"] = self.review_code_changes(self.task_id)
        
        # 3. 运行测试
        results["tests"] = self.run_tests()
        
        # 4. 生成测试报告
        test_report = self.generate_test_report(results)
        results["test_report"] = test_report
        
        # 5. 判断是否通过
        results["passed"] = (
            results["report_check"].get("valid", False) and
            not results["code_review"].get("has_sensitive_changes", False) and
            results["tests"].get("status") != "failed"
        )
        
        return results


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Tester Agent")
    parser.add_argument("--path", default=".", help="项目路径")
    parser.add_argument("--task-id", required=True, help="任务 ID")
    
    args = parser.parse_args()
    
    agent = TesterAgent(args.path, args.task_id)
    results = agent.execute()
    
    print(f"\n{'='*50}")
    print(f"测试结果：{'✅ 通过' if results['passed'] else '❌ 失败'}")
    print(f"测试报告：{results.get('test_report', 'N/A')}")


if __name__ == "__main__":
    main()
