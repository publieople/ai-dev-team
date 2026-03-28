# 任务卡片协议

## 任务卡片结构

```typescript
interface TaskCard {
  // 标识
  tid: string;           // 任务ID: t-{uuid}
  pid: string;           // 父任务ID（可选）
  
  // 分类
  type: TaskType;
  priority: Priority;
  
  // 上下文
  context: TaskContext;
  
  // 交付物
  deliverables: string[];
  
  // 控制
  max_retries: number;
  timeout: string;       // 如 "2h", "30m"
  
  // 元数据
  created: number;       // 时间戳
  updated: number;
}

type TaskType = 
  | "feature"      // 新功能
  | "bugfix"       // 修复bug
  | "refactor"     // 重构
  | "test"         // 测试相关
  | "doc"          // 文档
  | "research";    // 技术调研

type Priority = 
  | "critical"     // 阻塞性问题
  | "high"         // 重要功能
  | "normal"       // 常规任务
  | "low";          // 优化建议

interface TaskContext {
  title: string;         // 任务标题
  description: string;   // 详细描述
  files: string[];       // 相关文件路径
  constraints: string[]; // 约束条件
  references: string[];  // 参考文档/链接
}
```

## 完整示例

```json
{
  "tid": "t-a1b2c3d4",
  "pid": null,
  "type": "feature",
  "priority": "high",
  "context": {
    "title": "添加用户登录功能",
    "description": "实现基于JWT的用户认证系统，支持token刷新",
    "files": [
      "src/auth.ts",
      "src/middleware/auth.ts",
      "tests/auth.test.ts"
    ],
    "constraints": [
      "使用JWT进行认证",
      "支持access token和refresh token",
      "token过期时间为15分钟"
    ],
    "references": [
      "docs/auth-spec.md",
      "https://jwt.io/introduction"
    ]
  },
  "deliverables": [
    "实现JWT认证逻辑",
    "添加认证中间件",
    "编写单元测试",
    "更新API文档"
  ],
  "max_retries": 3,
  "timeout": "2h",
  "created": 1711612800,
  "updated": 1711612800
}
```

## TOON压缩格式

存储时使用缩写：

```json
{
  "tid": "t-a1b2c3d4",
  "type": "feat",
  "pri": "high",
  "ctx": {
    "t": "添加用户登录功能",
    "d": "实现基于JWT的用户认证系统",
    "f": ["src/auth.ts"],
    "c": ["使用JWT"],
    "r": ["docs/auth-spec.md"]
  },
  "del": ["实现JWT", "添加中间件", "单元测试"],
  "retry": 3,
  "to": "2h",
  "ct": 1711612800,
  "ut": 1711612800
}
```

## 子Agent执行报告

任务完成后生成：

```json
{
  "tid": "t-a1b2c3d4",
  "agent": "dev-001",
  "status": "success|failed|timeout",
  "summary": "完成JWT认证实现",
  "changes": {
    "modified": ["src/auth.ts"],
    "created": ["src/middleware/auth.ts"],
    "deleted": []
  },
  "tests": {
    "run": 5,
    "passed": 5,
    "failed": 0
  },
  "issues": [],
  "suggestions": ["建议添加rate limit"],
  "time_spent": "1h30m"
}
```

## 任务流转消息

主Agent ↔ 子Agent 通信格式：

**指派任务：**
```json
{
  "action": "assign",
  "task": { /* TaskCard */ },
  "workspace": "/path/to/project"
}
```

**任务完成：**
```json
{
  "action": "complete",
  "tid": "t-a1b2c3d4",
  "report": { /* ExecutionReport */ }
}
```

**任务失败：**
```json
{
  "action": "fail",
  "tid": "t-a1b2c3d4",
  "error": "编译失败",
  "logs": "...",
  "attempt": 2
}
```
