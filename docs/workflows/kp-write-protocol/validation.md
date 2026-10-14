# Validation

## 方法
- 回归测试：`backend/tests/test_question_domain.py` 新增 4 个用例（PUT 同步、PATCH 同步、PUT 省略不触碰、PUT 清空两表）。
- 运行：经官方守卫
  `python3 scripts/week4-scratch-guard.py run --db-name astra_week4_ci -- zsh -c 'cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_question_domain.py -q'`
- 全量回归：`pytest tests/ -q`。

## 证据
```text
单文件： tests/test_question_domain.py → 9 passed
全量：   949 passed, 9 skipped, 0 failed (前基线 945；+4 新用例)
red 证明： 回退服务改动后 PUT 同步用例失败 —— get_question 返回旧 KP [507] 而非新 [508]
```

## 变更
- `backend/app/services/question_service.py`：新增共享操作 `_replace_question_knowledge_points`，create/PUT/PATCH 三处调用。
- `backend/tests/test_question_domain.py`：+4 回归用例。

## 独立审查（另一 agent，只读）
- **VERDICT: PASS**。确认 A04 漂移对全部在范围内的生产写入者已闭合；回归测试确实在修复前失败。
- Findings 处置：
  1. `draft_service.py:322-335` 也双写两表（当前一致、无漂移）；未改为调用 helper（避免跨模块耦合），已在 helper docstring 中更正"所有路径"的过强表述。列为后续可选统一。
  2. PUT 会将被保留 KP 的 role/sort_order 重置为默认——**有意**（PUT 载荷无 role 概念，design.md 已定），与旧行为差异已记录。
  3. 仅 PUT 覆盖 → **已补** PATCH/省略/清空 用例。
  4. PATCH 重复 KP id 未去重（PK 冲突）——**既有问题**，非本次回归；后续可加校验。
  5. 存量漂移数据未回填——**明确不在范围**（属 G2 迁移，需单独授权）。
  6. 本文档此前未更新 → **已更新**。

## 状态
- T1–T6：完成（PASS）。T7 提交：进行中。
