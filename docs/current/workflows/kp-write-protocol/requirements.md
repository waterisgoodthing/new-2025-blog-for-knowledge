# Requirements

## 问题（已核实）
`backend/app/services/question_service.py`：
- `create_question`（:105–120）同时写 `QuestionKnowledgePoint`（专用）与 `KnowledgePointLink`（多态）。
- `update_question`（PUT，:312–326）**只**重写 `KnowledgePointLink`，不动 `QuestionKnowledgePoint`。
- `update_canonical_question`（PATCH，:404–422）两者都重写。
- 读取 `get_question`（:192–219）**优先** `QuestionKnowledgePoint`；`list_questions` 过滤（:157–161）与 practice 均用 `QuestionKnowledgePoint`。

→ PUT 修改 KP 后：专用关系停留在旧集合，读取/筛选/练习与 PUT 意图**分叉**（A04 CONFIRMED_DRIFT）。

## 需求
1. Question 的 KP 写入在 create/PUT/PATCH 三处**使用同一操作**，同时维护专用关系（规范）与多态投影。
2. 专用关系 `QuestionKnowledgePoint` 为读取/筛选/练习的规范来源；`KnowledgePointLink` 仅作兼容投影，二者保持同步。
3. 不删除任何表、不改 schema、不做数据迁移；不擅自回填存量分叉数据。
4. 保持对外 API 形状与既有 PUT/PATCH 语义（版本冲突、404 等）不变。

## 验收
- PUT 修改 KP 后，`get_question().knowledge_point_ids` 反映新集合。
- `QuestionKnowledgePoint` 与 `KnowledgePointLink` 两表内容一致（同一集合）。
- create/PUT/PATCH 三者结果一致。
- 现有后端测试不回退。
