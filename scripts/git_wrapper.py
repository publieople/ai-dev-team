#!/usr/bin/env python3
"""
AI Dev Team - Git可追溯封装
提供带元数据的提交功能
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_git(args, cwd=None, check=True):
    """运行git命令"""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check
    )
    return result

def get_repo_info(cwd=None):
    """获取仓库信息"""
    try:
        remote = run_git(["remote", "get-url", "origin"], cwd=cwd, check=False)
        branch = run_git(["branch", "--show-current"], cwd=cwd)
        return {
            "remote": remote.stdout.strip() if remote.returncode == 0 else None,
            "branch": branch.stdout.strip()
        }
    except:
        return {"remote": None, "branch": None}

def create_commit(
    message: str,
    task_id: str,
    agent_id: str,
    plan_file: str = None,
    report_file: str = None,
    commit_type: str = "feat",
    cwd=None
):
    """
    创建带AI元数据的Git提交
    
    Args:
        message: 提交信息主体
        task_id: 任务ID
        agent_id: Agent标识
        plan_file: 规划文件路径
        report_file: 执行报告路径
        commit_type: 提交类型 (feat/fix/docs/test/refactor)
        cwd: 工作目录
    """
    
    # 构建提交信息
    subject = f"[AI-{task_id}] {commit_type}: {message}"
    
    # 构建元数据
    metadata = {
        "AI-Task": task_id,
        "AI-Agent": agent_id,
        "AI-Time": datetime.now().isoformat(),
    }
    
    if plan_file:
        metadata["AI-Plan"] = plan_file
    if report_file:
        metadata["AI-Report"] = report_file
    
    # 构建完整提交信息
    body = "\n".join([f"{k}: {v}" for k, v in metadata.items()])
    full_message = f"{subject}\n\n{body}"
    
    # 执行提交
    run_git(["add", "-A"], cwd=cwd)
    run_git(["commit", "-m", full_message], cwd=cwd)
    
    return {
        "hash": run_git(["rev-parse", "HEAD"], cwd=cwd).stdout.strip(),
        "message": subject,
        "metadata": metadata
    }

def find_ai_commits(task_id: str = None, cwd=None):
    """查找AI提交"""
    if task_id:
        pattern = f"[AI-{task_id}]"
    else:
        pattern = "[AI-"
    
    result = run_git(
        ["log", "--grep", pattern, "--format=%H|%s|%ai", "--all"],
        cwd=cwd,
        check=False
    )
    
    commits = []
    for line in result.stdout.strip().split("\n"):
        if "|" in line:
            hash_val, subject, date = line.split("|", 2)
            commits.append({
                "hash": hash_val,
                "subject": subject,
                "date": date
            })
    
    return commits

def get_commit_info(commit_hash: str, cwd=None):
    """获取提交详细信息"""
    result = run_git(
        ["show", commit_hash, "--format=%H|%s|%b|%ai", "--quiet"],
        cwd=cwd
    )
    
    parts = result.stdout.split("|", 3)
    if len(parts) >= 3:
        # 解析元数据
        metadata = {}
        for line in parts[2].split("\n"):
            if line.startswith("AI-") and ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
        
        return {
            "hash": parts[0],
            "subject": parts[1],
            "metadata": metadata,
            "date": parts[3] if len(parts) > 3 else None
        }
    
    return None

def revert_ai_commit(task_id: str, cwd=None):
    """回滚AI提交"""
    commits = find_ai_commits(task_id, cwd=cwd)
    if not commits:
        return None
    
    # 找到最新提交并回滚
    latest = commits[0]["hash"]
    run_git(["revert", "--no-commit", latest], cwd=cwd)
    
    return {
        "reverted_commit": latest,
        "status": "reverted"
    }

if __name__ == "__main__":
    import sys
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "commit":
        # 测试提交
        result = create_commit(
            message="测试AI提交",
            task_id="t-test001",
            agent_id="dev-test",
            commit_type="test"
        )
        print(f"提交成功: {result['hash'][:8]}")
    
    elif cmd == "list":
        task_id = sys.argv[2] if len(sys.argv) > 2 else None
        commits = find_ai_commits(task_id)
        for c in commits:
            print(f"{c['hash'][:8]} | {c['subject']} | {c['date']}")
    
    elif cmd == "info":
        commit_hash = sys.argv[2]
        info = get_commit_info(commit_hash)
        print(json.dumps(info, indent=2))
    
    else:
        print("用法: git_wrapper.py [commit|list|info]")
