# PR-09-verify-api findings (HTTP contract / permissions / freeze / source / browser)

agent: PR-09-verify-api · role: verifier · date: 2026-09-24
scope: HTTP 契约/权限/冻结/源码搜索/真实浏览器。迁移/ledger 归另一验证员，本文不裁决 G2。

## FINDING-01 HIGH — admin mistake 写操作（含 publish/unpublish）HTTP 500

- 现象：`PATCH /api/admin/mistakes/{id}/visibility`（正确 version 且 visibility 实际变更）、`PUT /api/admin/mistakes/{id}`、`DELETE /api/admin/mistakes/{id}`（archive）均 500 `Internal server error`。
- 对照（同库同会话）：`GET /api/admin/mistakes/{id}`、`GET /api/admin/mistakes` 200；错误 version 409；**noop PATCH（visibility 已是目标值，不触发 flush）200**。
- 根因：`backend/app/services/mistake_service.py` `update_mistake_visibility`/`update_mistake`/`archive_mistake` 对 ORM 行 mutate + `flush()`（`mistakes.updated_at` 为 server `onupdate=func.now()`，flush 后该列过期）后返回 ORM 挂载的 `MistakeRecord`；FastAPI `response_model` 序列化在同步上下文惰性加载过期列 → `sqlalchemy.exc.MissingGreenlet` → 被 `request_observability` 吞成 500。
- 影响：
  - C.2「admin 发布/下架后公共页反映」**API 路径不可用**（`src/app/manage/(workspace)/mistakes/components/mistake-detail.tsx` 的 `updateMistakeVisibility` 即此端点）。
  - PR-09 新增的 admin-only visibility 变更（验收项）在成功路径上不可达；仅 409/401 负测可过。
  - PUT/DELETE 同因同果（PUT/DELETE 为既有路径，可能先于 PR-09 存在，但 PR-09 的 PATCH 新路径必踩）。
- 证据：`evidence/api/pr-09-api-http-matrix.txt`（A.x 行 + repro 输出）、`evidence/tests/pr-09-api-pytest.txt::test_visibility_correct_version_toggles`、`evidence/browser/pr-09-api-scenarios.md`。
- 建议（未修，产品代码不在本验证员写范围）：`get_mistake` 在返回前 `await session.refresh(m)`，或服务层直接构造响应 DTO（脱离 ORM 会话），或 `expire_on_commit=False` + 序列化前刷新；并补一条「成功 PATCH visibility → 200」的 HTTP 测试（当前实现方 `test_pr09_routes.py` 仅纯/静态断言，无成功路径 HTTP 测试）。

## FINDING-02 LOW — `test_pr09_verify_http.py` 与本矩阵重叠且自身含 EventLoop 隐患

- 现象：仓库已存在 `backend/tests/test_pr09_verify_http.py`（非本验证员写范围）使用共享 `async_session` + 多次 `asyncio.run`，与 TestClient 事件循环混用会触发 `attached to a different loop`；其 `test_compat_read_search` 用 `POST /api/search`（实际为 `POST /api/admin/search`）。
- 影响：测试卫生；不影响产品行为。本矩阵以 `backend/tests/test_pr09_verify_api_contract.py`（每 seed 独立 engine、fresh scratch DB）为准。
- 建议：删除或改写重复文件（由主 agent 决定）。

## 非缺陷记录

- 兼容读 K 抽样（notes list / admin search / review queue / mistake note get）200；search 与 review queue 需 admin session（与现契约一致，非回归）。
- 冻结 F-1～F-9 全部 410 + `code=legacy_mistake_write_frozen`；note 型创建仍 201（控制组）。
- 公共 DTO allowlist 恰 11 项，pydantic/TS/`week3_contracts_support` 三方集合相等；禁列不出现。
