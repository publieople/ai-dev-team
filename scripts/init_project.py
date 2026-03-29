#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Dev Team - 项目初始化脚本
主 Agent 在检测到新 Git 项目时自动调用
"""

import os
import json
from pathlib import Path
from datetime import datetime

def init_ai_dev_team(project_path: str = "."):
    """初始化 AI Dev Team 项目结构"""
    
    project_path = Path(project_path).resolve()
    
    # 检查是否是 Git 仓库
    if not (project_path / ".git").exists():
        print("❌ 错误：当前目录不是 Git 仓库")
        print("请先运行：git init")
        return False
    
    ai_dir = project_path / ".ai-dev-team"
    
    # 检查是否已初始化
    if ai_dir.exists():
        print(f"⚠️  警告：{ai_dir} 已存在")
        response = input("是否重新初始化？(y/n): ").strip().lower()
        if response != 'y':
            print("已取消")
            return False
    
    # 创建目录结构
    dirs = ["tasks", "reports", "docs", "logs"]
    for d in dirs:
        (ai_dir / d).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建目录：.ai-dev-team/{d}/")
    
    # 创建默认配置
    config = {
        "workflow": {
            "auto_approve": False,
            "require_human_test": True,
            "max_concurrent_agents": 1,
            "max_retries": 3
        },
        "review": {
            "schedule": "0 20 * * *",
            "timezone": "Asia/Shanghai"
        },
        "git": {
            "auto_commit": True,
            "traceability": True
        }
    }
    
    config_file = ai_dir / "config.json"
    config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ 创建配置：.ai-dev-team/config.json")
    
    # 创建初始状态
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

1. 主 Agent 会自动分析项目
2. 生成任务列表
3. 发送规划请人类批准
4. 批准后开始开发

## 验收时间

每天 20:00（Asia/Shanghai）自动发送验收请求

---

*由 AI Dev Team 管理*
"""
    
    readme_file = ai_dir / "README.md"
    readme_file.write_text(readme_content, encoding="utf-8")
    print(f"  ✓ 创建说明：.ai-dev-team/README.md")
    
    print(f"\n✅ AI Dev Team 初始化完成！")
    print(f"📁 项目目录：{ai_dir}")
    print(f"\n下一步：主 Agent 将自动分析项目并生成任务列表")
    
    return True

if __name__ == "__main__":
    import sys
    project_path = sys.argv[1] if len(sys.argv) > 1 else "."
    success = init_ai_dev_team(project_path)
    sys.exit(0 if success else 1)
