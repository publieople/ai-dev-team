#!/usr/bin/env python3
"""
AI Dev Team - Researcher Agent
负责收集官方文档、技术调研、维护文档库
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

class ResearcherAgent:
    """文档研究员 Agent"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.ai_dir = self.project_path / ".ai-dev-team"
        self.docs_dir = self.ai_dir / "docs"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
    def search_context7(self, library: str, query: str) -> Optional[Dict]:
        """
        使用 Context7 搜索文档
        
        Returns:
            搜索结果（库列表）
        """
        context7_dir = Path(__file__).parent.parent.parent / "context7"
        if not context7_dir.exists():
            print("⚠️  Context7 未安装")
            return None
        
        try:
            result = subprocess.run(
                ["npx", "tsx", "query.ts", "search", library, query],
                cwd=str(context7_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析输出（简化处理，实际应该解析 JSON）
                return {
                    "raw_output": result.stdout,
                    "library": library,
                    "query": query
                }
            else:
                print(f"⚠️  Context7 搜索失败：{result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print("⚠️  Context7 搜索超时")
            return None
        except Exception as e:
            print(f"⚠️  Context7 错误：{e}")
            return None
    
    def get_context7_context(self, library_id: str, query: str) -> Optional[Dict]:
        """
        使用 Context7 获取详细文档上下文
        
        Args:
            library_id: 库 ID（如 "vercel/next.js"）
            query: 查询问题
            
        Returns:
            文档内容
        """
        context7_dir = Path(__file__).parent.parent.parent / "context7"
        if not context7_dir.exists():
            return None
        
        try:
            result = subprocess.run(
                ["npx", "tsx", "query.ts", "context", library_id, query],
                cwd=str(context7_dir),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "content": result.stdout,
                    "library_id": library_id,
                    "query": query,
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                print(f"⚠️  Context7 获取上下文失败：{result.stderr}")
                return None
        except Exception as e:
            print(f"⚠️  Context7 错误：{e}")
            return None
    
    def web_search(self, query: str, count: int = 5) -> List[Dict]:
        """
        使用 web_search 搜索（通过 OpenClaw 工具）
        
        注意：这个函数需要主 Agent 调用 sessions_send 来执行
        这里只提供接口定义
        """
        # 实际实现需要通过 OpenClaw 工具调用
        # 这里返回占位符
        return []
    
    def cache_document(self, title: str, content: str, source: str = None, 
                       tags: List[str] = None) -> str:
        """
        缓存文档到本地
        
        Returns:
            文档文件路径
        """
        # 生成文件名
        safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title.lower())
        filename = f"{safe_title}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        filepath = self.docs_dir / filename
        
        # 构建文档元数据
        metadata = {
            "title": title,
            "source": source,
            "tags": tags or [],
            "cached_at": datetime.now().isoformat()
        }
        
        # 写入文档
        markdown = f"""---
title: {title}
source: {source or "未知"}
cached_at: {metadata['cached_at']}
tags: {', '.join(tags) if tags else ""}
---

{content}

---

*文档由 AI Dev Team Researcher Agent 自动缓存*
"""
        filepath.write_text(markdown, encoding="utf-8")
        print(f"📚 文档已缓存：{filepath}")
        return str(filepath)
    
    def search_local_docs(self, query: str) -> List[Dict]:
        """
        搜索本地文档缓存
        
        Returns:
            匹配的文档列表
        """
        results = []
        
        for doc_file in self.docs_dir.glob("*.md"):
            content = doc_file.read_text(encoding="utf-8")
            
            # 简单关键词匹配（可以改进为向量搜索）
            query_terms = query.lower().split()
            match_count = sum(1 for term in query_terms if term in content.lower())
            
            if match_count > 0:
                # 解析 frontmatter
                metadata = {"path": str(doc_file), "match_score": match_count}
                
                # 简单提取标题
                for line in content.split("\n")[:10]:
                    if line.startswith("title:"):
                        metadata["title"] = line.split(":", 1)[1].strip()
                        break
                
                results.append(metadata)
        
        # 按匹配度排序
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results
    
    def create_api_reference(self, library: str, topics: List[str]) -> str:
        """
        创建 API 参考文档
        
        Args:
            library: 库名称（如 "vercel/next.js"）
            topics: 主题列表
            
        Returns:
            文档路径
        """
        doc_title = f"{library} API 参考"
        full_content = f"# {doc_title}\n\n"
        full_content += f"**生成时间:** {datetime.now().isoformat()}\n"
        full_content += f"**库:** {library}\n\n"
        full_content += "---\n\n"
        
        for topic in topics:
            print(f"📖 收集文档：{topic}")
            context = self.get_context7_context(library, topic)
            
            if context:
                full_content += f"## {topic}\n\n"
                full_content += context["content"]
                full_content += "\n\n---\n\n"
        
        # 缓存完整文档
        filepath = self.cache_document(
            title=doc_title,
            content=full_content,
            source=library,
            tags=["api", "reference", library]
        )
        
        return filepath
    
    def research_task(self, task: Dict) -> Dict:
        """
        执行调研任务
        
        Args:
            task: 任务信息
            
        Returns:
            调研结果
        """
        print(f"\n🔍 开始调研任务：{task.get('title', 'N/A')}")
        
        result = {
            "task_id": task.get("tid"),
            "researched_at": datetime.now().isoformat(),
            "sources_used": [],
            "documents_cached": [],
            "findings": []
        }
        
        # 解析任务需求
        description = task.get("description", "")
        
        # 识别技术栈
        tech_stack = task.get("context", {}).get("tech_stack", [])
        
        # 为每个技术收集文档
        for tech in tech_stack:
            print(f"  → 收集 {tech} 文档...")
            
            # 先搜索本地缓存
            local_docs = self.search_local_docs(tech)
            if local_docs:
                print(f"    ✓ 找到 {len(local_docs)} 篇本地文档")
                result["sources_used"].append(f"local:{tech}")
            else:
                # 使用 Context7
                context = self.get_context7_context(tech, "getting started")
                if context:
                    doc_path = self.cache_document(
                        title=f"{tech} 入门指南",
                        content=context["content"],
                        source=tech,
                        tags=["getting-started", tech]
                    )
                    result["documents_cached"].append(doc_path)
                    result["sources_used"].append(f"context7:{tech}")
        
        # 生成调研报告
        report_file = self.ai_dir / "reports" / f"research-{task.get('tid')}.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        report_md = self._generate_research_report(result)
        report_file.write_text(report_md, encoding="utf-8")
        result["report_file"] = str(report_file)
        
        print(f"✅ 调研完成！报告：{report_file}")
        return result
    
    def _generate_research_report(self, result: Dict) -> str:
        """生成调研报告"""
        md = f"""# 调研报告

**任务 ID:** {result['task_id']}
**调研时间:** {result['researched_at']}

---

## 使用的数据源

"""
        for source in result["sources_used"]:
            md += f"- {source}\n"
        
        md += f"""
## 缓存的文档

"""
        for doc in result["documents_cached"]:
            md += f"- `{doc}`\n"
        
        md += f"""
## 发现

{chr(10).join(result.get('findings', ['无特别发现']))}

---

## 下一步

Developer Agent 可以参考以上文档进行开发。

*报告由 AI Dev Team Researcher Agent 生成*
"""
        return md


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Researcher Agent")
    parser.add_argument("command", choices=["search", "context", "cache", "research"],
                        help="命令")
    parser.add_argument("--path", default=".", help="项目路径")
    parser.add_argument("--library", help="库名称")
    parser.add_argument("--query", help="查询内容")
    parser.add_argument("--task", help="任务 JSON 文件")
    
    args = parser.parse_args()
    
    agent = ResearcherAgent(args.path)
    
    if args.command == "search":
        if not args.library or not args.query:
            print("❌ 需要指定 --library 和 --query")
            sys.exit(1)
        result = agent.search_context7(args.library, args.query)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.command == "context":
        if not args.library or not args.query:
            print("❌ 需要指定 --library 和 --query")
            sys.exit(1)
        result = agent.get_context7_context(args.library, args.query)
        print(result["content"] if result else "无结果")
    
    elif args.command == "cache":
        # 从 stdin 读取内容
        content = sys.stdin.read()
        filepath = agent.cache_document(
            title=args.query or "未命名文档",
            content=content,
            source=args.library
        )
        print(f"已缓存：{filepath}")
    
    elif args.command == "research":
        if not args.task:
            print("❌ 需要指定 --task")
            sys.exit(1)
        with open(args.task, "r", encoding="utf-8") as f:
            task = json.load(f)
        result = agent.research_task(task)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
