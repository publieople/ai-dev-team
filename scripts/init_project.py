#!/usr/bin/env python3
"""
AI Dev Team - 项目初始化脚本
创建 .ai-dev-team/ 目录结构和初始配置
"""

import os
import sys
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "v": 1,
    "project": {"n": "", "t": "auto", "ts": []},
    "wf": {"aa": False, "rht": True, "mca": 1, "dto": "2h", "mr": 3},
    "esc": {"th": 3, "cf": 3, "ta": "esc"},
    "rep": {"fmt": "md", "ds": True, "id": True},
    "git": {"ac": True, "cp": "[AI]", "tr": True, "bs": "direct"},
    "toon": {"en": True, "cmp": "agg"}
}

def init_project(project_path="."):
    """初始化AI开发团队项目"""
    
    project_path = Path(project_path).resolve()
    ai_dir = project_path / ".ai-dev-team"
    
    # 检查Git仓库
    git_dir = project_path / ".git"
    if not git_dir.exists():
        print("[ERROR] 当前目录不是Git仓库")
        print("   请先运行: git init")
        sys.exit(1)
    
    # 创建目录结构
    dirs = ["tasks", "reports", "logs"]
    for d in dirs:
        (ai_dir / d).mkdir(parents=True, exist_ok=True)
    
    # 创建配置文件
    config_file = ai_dir / "config.json"
    if not config_file.exists():
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        print(f"[OK] 创建配置: {config_file}")
    
    # 创建状态文件
    state_file = ai_dir / "state.json"
    if not state_file.exists():
        initial_state = {"v": 1, "tasks": {}, "queue": [], "active": None}
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(initial_state, f, indent=2)
        print(f"[OK] 创建状态: {state_file}")
    
    # 添加到.gitignore
    gitignore = project_path / ".gitignore"
    ignore_entry = ".ai-dev-team/logs/\n"
    
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8")
        if ignore_entry.strip() not in content:
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write(f"\n# AI Dev Team\n{ignore_entry}")
            print(f"[OK] 更新 .gitignore")
    else:
        gitignore.write_text(f"# AI Dev Team\n{ignore_entry}", encoding="utf-8")
        print(f"[OK] 创建 .gitignore")
    
    print(f"\n[DONE] 项目初始化完成!")
    print(f"   目录: {ai_dir}")
    print(f"\n下一步: 运行 '@ai-dev-team analyze' 开始项目分析")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    init_project(path)
