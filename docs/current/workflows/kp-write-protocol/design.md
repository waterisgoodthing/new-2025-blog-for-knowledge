# Design

## 方案
在 `question_service.py` 抽取共享操作：

```python
async def _replace_question_knowledge_points(session, question_id, links) -> None:
    # links: [{"knowledge_point_id": int, "role"?: str, "sort_order"?: int}]
    # 1) 删除多态投影 (target_type='question')
    # 2) 删除专用关系 QuestionKnowledgePoint
    # 3) 重新插入两者（保持一致）
```

调用点：
- `create_question`：用 `payload.knowledge_point_links` 构造 links。
- `update_question`（PUT）：当 `"knowledge_point_ids" in changes`，用 `validated.knowledge_point_ids` 构造 links（role 默认 primary，sort_order 默认 0）。
- `update_canonical_question`（PATCH）：用 `validated.knowledge_point_links` 构造 links。

## 备选与取舍
- 备选 A：只改 PUT 也写专用关系（局部）；不选——三处仍各写一份，未来会再次分叉。
- 备选 B：把专用关系完全废弃、只留多态；不选——读取/练习/filter 都依赖专用表，且属数据迁移。
- 选择：共享 helper + 专用关系为规范（与 DR-B01 建议一致）。

## 边界
- 不改 schema/迁移；不回填存量数据（另需授权，属 G2）。
- 事务与锁语义沿用现有（`with_for_update` + version 校验）。
- 若 PUT 未提供 `knowledge_point_ids`，不触碰 KP 关系（保持 `exclude_unset` 语义）。
