# 故障排查

## 常见问题

### 主Agent无法启动

**症状：** `@ai-dev-team init` 无响应

**排查：**
1. 检查当前目录是否为Git仓库
   ```bash
   git status
   ```
2. 检查是否有写入权限
   ```bash
   touch .ai-dev-team-test && rm .ai-dev-team-test
   ```

**解决：**
- 非Git仓库 → 先 `git init`
- 无权限 → 更换目录或提升权限

### 子Agent超时

**症状：** 任务长时间无响应

**排查：**
1. 查看任务状态
   ```bash
   @ai-dev-team status
   ```
2. 检查Agent日志
   ```bash
   cat .ai-dev-team/logs/agent-dev-001.log
   ```

**解决：**
- 正常现象（复杂任务）→ 等待或增加timeout
- 真正卡死 → 主Agent自动终止并重新指派

### 任务连续失败

**症状：** 同一任务重试3次仍失败

**排查：**
1. 查看执行报告
   ```bash
   cat .ai-dev-team/reports/execution-t-xxx.md
   ```
2. 检查错误类型
   - 编译错误 → 环境问题
   - 测试失败 → 实现问题
   - 超时 → 任务过大

**解决：**
- 环境问题 → 主Agent生成环境修复任务
- 实现问题 → 上报人类，可能需求不明确
- 任务过大 → 拆分更细粒度任务

### Git提交冲突

**症状：** AI提交与人类提交冲突

**解决：**
1. 主Agent自动rebase
2. 如无法自动解决 → 上报人类

### 状态机损坏

**症状：** state.json 格式异常

**恢复：**
1. 从Git历史恢复
   ```bash
   git checkout HEAD~1 -- .ai-dev-team/state.json
   ```
2. 手动修复后重新加载

## 调试命令

```bash
# 查看完整状态
@ai-dev-team status --verbose

# 查看特定任务
@ai-dev-team task t-xxx

# 强制重置状态（谨慎）
@ai-dev-team reset --hard

# 导出完整日志
@ai-dev-team export-logs
```

## 上报模板

向人类上报问题时使用：

```markdown
## 问题报告

**任务ID:** t-xxx
**类型:** 开发失败 / 系统异常 / 其他

**现象:**
[描述发生了什么]

**已尝试方案:**
1. [方案1] - 结果
2. [方案2] - 结果

**建议选项:**
- A: [选项A描述]
- B: [选项B描述]

**需要人类决策:**
[明确的问题]
```

## 联系支持

如问题无法解决：
1. 导出日志：`@ai-dev-team export-logs`
2. 提交到项目Issue
