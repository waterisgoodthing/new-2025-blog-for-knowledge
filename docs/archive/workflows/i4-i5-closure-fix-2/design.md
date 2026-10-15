# 设计

## 偏好契约

支持区块固定为：

```text
today    今日任务
activity 最近活动
stats    内容统计
storage  附件状态
```

`section_order` 必须包含四个值且各出现一次；Dashboard 按该顺序渲染。`hidden_sections` 只能包含支持值且不得重复。`today` 与 `activity` 定义为学习行动区块，至少一个必须保持可见；因此隐藏 `today` 与 `activity` 的请求必须在前端阻止、后端以 422 拒绝。

前端和后端各自执行同一组显式规则：TypeScript 负责编辑器即时约束与提示，Pydantic 负责真实 API 安全边界。两侧不依赖 JSON 推断，也不以隐藏数量单独推导安全性。

## Dashboard 渲染

Dashboard 将区块定义为带 `id`、标题和渲染函数的显式映射，先按 profile 偏好排序，再过滤隐藏区块。偏好缺失、非法或 profile 加载失败时继续使用默认顺序和默认可见集合；已有 I4 学习行动区块仍必须渲染。

## empty 与系统健康

`empty` 表示依赖正常但当前没有数据，不是故障：

| section | ready | empty | unavailable/unknown |
|---|---|---|---|
| learning/activity | system.database=`ok` | system.database=`ok` | system.database=`unavailable` |
| storage | system.storage=`ok` | system.storage=`ok` | system.storage=`unknown` |

系统服务能返回安全摘要时保持 `service=ok`。数据库健康按数据库区块的最严重状态聚合，不能因某个空区块误报故障，也不能因局部 SQL 失败继续报健康。

## 测试与证据

- 后端：局部 learning/activity 失败、storage unknown、全空数据、正常依赖完成 commit、异常 rollback/close 后恢复、偏好 PUT 后 GET 刷新一致。
- 前端：偏好排序/隐藏真实 DOM 顺序、学习行动区块保护、empty 健康文案、保存后重新拉取并刷新 Dashboard。
- 浏览器：管理员会话下先设置非默认顺序并隐藏一个非行动区块，刷新 `/manage/dashboard`，保存桌面与移动证据，断言 DOM 顺序与不可见区块；再恢复默认偏好并记录结果。
