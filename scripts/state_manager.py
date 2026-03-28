#!/usr/bin/env python3
"""
AI Dev Team - 状态机管理
提供状态流转、持久化、查询功能
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, List
from enum import Enum

class State(Enum):
    DISCOVERED = "D"
    ANALYZING = "A"
    PLANNING = "P"
    PENDING_APPROVAL = "PA"
    ASSIGNED = "AS"
    IN_PROGRESS = "IP"
    TESTING = "T"
    PENDING_HUMAN_TEST = "PHT"
    ESCALATED = "E"
    HUMAN_ESCALATION = "HE"
    COMPLETED = "C"
    CANCELLED = "X"
    REASSIGNING = "R"

STATE_TRANSITIONS = {
    State.DISCOVERED: [State.ANALYZING, State.PENDING_APPROVAL],  # 允许直接批准
    State.ANALYZING: [State.PLANNING, State.HUMAN_ESCALATION],
    State.PLANNING: [State.PENDING_APPROVAL],
    State.PENDING_APPROVAL: [State.ASSIGNED, State.CANCELLED],
    State.ASSIGNED: [State.IN_PROGRESS, State.REASSIGNING],
    State.IN_PROGRESS: [State.TESTING, State.ESCALATED],
    State.TESTING: [State.PENDING_HUMAN_TEST, State.IN_PROGRESS],
    State.PENDING_HUMAN_TEST: [State.COMPLETED, State.ANALYZING],
    State.ESCALATED: [State.REASSIGNING, State.HUMAN_ESCALATION],
    State.REASSIGNING: [State.ASSIGNED],
    State.HUMAN_ESCALATION: list(State),  # 人类可转移到任意状态
    State.COMPLETED: [],
    State.CANCELLED: []
}

class StateManager:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.state_file = self.project_path / ".ai-dev-team" / "state.json"
        self._state = None
        self._load()
    
    def _load(self):
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                self._state = json.load(f)
        else:
            self._state = {"v": 1, "tasks": {}, "queue": [], "active": None}
    
    def _save(self):
        """保存状态"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2)
    
    def get_task(self, tid: str) -> Optional[Dict]:
        """获取任务"""
        return self._state["tasks"].get(tid)
    
    def create_task(self, task: Dict) -> str:
        """创建新任务"""
        tid = task.get("tid") or f"t-{int(time.time() * 1000)}"
        task["tid"] = tid
        task["s"] = State.DISCOVERED.value
        task["ct"] = int(time.time())
        task["ut"] = task["ct"]
        task["retry"] = 0
        
        self._state["tasks"][tid] = task
        self._state["queue"].append(tid)
        self._save()
        return tid
    
    def transition(self, tid: str, new_state: State, **kwargs) -> bool:
        """状态流转"""
        task = self.get_task(tid)
        if not task:
            return False
        
        current = State(task["s"])
        if new_state not in STATE_TRANSITIONS[current]:
            raise ValueError(f"非法状态转换: {current.value} -> {new_state.value}")
        
        task["s"] = new_state.value
        task["ut"] = int(time.time())
        task.update(kwargs)
        
        # 特殊处理
        if new_state == State.ASSIGNED:
            self._state["active"] = tid
        elif new_state in [State.COMPLETED, State.CANCELLED]:
            if self._state["active"] == tid:
                self._state["active"] = None
        
        self._save()
        return True
    
    def get_active_task(self) -> Optional[Dict]:
        """获取当前活跃任务"""
        tid = self._state.get("active")
        return self.get_task(tid) if tid else None
    
    def get_queue(self) -> List[str]:
        """获取任务队列"""
        return self._state["queue"]
    
    def list_tasks(self, state: Optional[State] = None) -> List[Dict]:
        """列出任务"""
        tasks = self._state["tasks"].values()
        if state:
            tasks = [t for t in tasks if t["s"] == state.value]
        return list(tasks)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        tasks = self._state["tasks"].values()
        return {
            "total": len(tasks),
            "completed": len([t for t in tasks if t["s"] == State.COMPLETED.value]),
            "active": len([t for t in tasks if t["s"] == State.IN_PROGRESS.value]),
            "pending": len([t for t in tasks if t["s"] == State.PENDING_APPROVAL.value]),
            "escalated": len([t for t in tasks if t["s"] == State.ESCALATED.value])
        }

if __name__ == "__main__":
    import sys
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    sm = StateManager()
    
    if cmd == "status":
        stats = sm.get_stats()
        print(f"任务统计: {stats}")
        active = sm.get_active_task()
        if active:
            print(f"活跃任务: {active['tid']} ({active['s']})")
    elif cmd == "list":
        state_filter = sys.argv[2] if len(sys.argv) > 2 else None
        if state_filter:
            tasks = sm.list_tasks(State(state_filter))
        else:
            tasks = sm.list_tasks()
        for t in tasks:
            print(f"{t['tid']}: {t['s']} - {t.get('ctx', {}).get('t', 'N/A')}")
