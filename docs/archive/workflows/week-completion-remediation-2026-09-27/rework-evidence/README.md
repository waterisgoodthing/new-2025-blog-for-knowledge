# 返工证据账本（B00–B07，本地隔离）

日期：2026-09-27。执行者：本线程主 Agent（primary_owner），按
[rework-plan.md](../rework-plan.md) 的 B00→B07 串行推进。本文件是对 *本轮返工* 本身
的证据索引，不覆盖 [execution-verification](../README.md) 的原始 FAIL 结论，也不把
本轮当作最终产品验收——B07 的独立复核与远端/生产证据仍单列。

当前状态索引见本目录 [STATUS.md](STATUS.md)；具体断言与命令见各条目。

## B00 现场保留

| 事项 | 结果 |
|---|---|
| 可恢复源码快照 | `/var/folders/.../opencode/b00-snapshot/rework-source-4a954ea.tar.gz`，112 MB |
| 快照 SHA-256 | `069cc22997e56724aaad72998ba2f6ff6971a2a0959b3265cfb14231002e4274`（见 `tarball.sha256`） |
| 恢复抽查 | `review-queue.tsx` 解包 diff 与工作树逐字节一致 → `RESTORE_OK` |
| 排除项 | `.git`、`node_modules`、`.next`、`.open-next`、`.venv`、`__pycache__`、`.env*`（保留 `.env.example`）、上传/缓存/数据库文件 |
| 会话内编写文件 | 本目录新增文档与 `b02-legacy-kp-candidate-report.sql`；产品代码改动见各条目 |

## B01 再答竞态（EV01 修复）

- 产品代码：`src/app/manage/(workspace)/review/review-queue.tsx`
  - 每个 review-item 维护请求代次计数（`generationRef`），打开/收起/换题/改答案/确认成功全部 bump；
  - `openReanswer`、`submitAnswer` 每次异步返回前校验 `isCurrent(itemId, generation)`，过期响应（成功或失败）一律丢弃；
  - `submitReview` 成功后也 bump，卸载重置代次（`mountedRef`）。
- 回归测试（`review-queue.test.tsx` 新增 3 例，9 passed）：
  1. 延迟的 A 判分在收起→重开选 B 后不得出现，且确认时不携带旧 attemptId（`submitReview` 第 4 参为 `undefined`）；
  2. 过期失败响应不得渲染错误横幅；
  3. 首次题目 load 未完成即被收起时，后续乱序考题不得覆盖。

## B02 KP 事实保留（补验收 + 只读候选报告）

- 回归测试：`tests/test_b02_kp_preservation.py`（全部独立事务+请求间隔读回）：
  自动错答继承问题 KP 快照→convert→mistake 保留；人工显式 `[]` 与显式替换权威；
  题目后改 KP 不回写已确认 mistake；rating0→review/lapse=1、practice 不计 review 再答；
  正确再答→review_count=2、lapse 不变；Dashboard/Practice 回读一致；
  非法学科/失效 KP 拒绝；重复 convert 幂等；版本冲突无副作用。
- 只读存量候选查询：[b02-legacy-kp-candidate-report.sql](b02-legacy-kp-candidate-report.sql)
  （已在隔离库证明可执行，纯 SELECT；含 `origin_kind`/source_attempt/debug 字段）。空集合按
  语义不判定丢失。

## B03 冻结遗漏（EV02 修复）

- 产品代码：
  - `taxonomy_service.delete_knowledge_point`：改 `SELECT … FOR UPDATE`，并在删除前 JOIN
    `note_knowledge_points × notes` 检查 legacy `type='mistake'`，命中则抛
    `LegacyMistakeWriteFrozen`（事务零副作用）。
  - `routers/knowledge_points.py`：把该异常映射为 **410 + `legacy_mistake_write_frozen`**。
  - `note_knowledge_point_service.link/unlink`：获取 KP 时加 `populate_existing` 读回最新状态
    （不加写锁——锁的方案在既有 pr12 并发两端连接重叠测试中超时）；只要删除侧持锁，任何 link
    在它提交前无法看到"半个删除"，即下面的组合仍序列化。
- 回归测试：`tests/test_b03_kp_delete_freeze.py`：
  真实管理员 HTTP DELETE 返回 410 且新会话读回关系仍在；service 层同样冻结；并发 link 提交
  后 delete 等到检查点（与 connection 复用存在既有 pr12 测试锁冲突，已改为删除侧单向持锁，
  见 STATUS.md）；无关联 KP 正常删除。

## B04 schema 双门禁（EV03 修复）

- 新增 `app/models/schema_catalog_gate.py`（独立命令，`python -m app.models.schema_catalog_gate`，
  `--write` 生成 manifest）与版本化清单 `app/models/schema_manifest.json`（revision 绑定 head）。
- 比较覆盖：受治理 schema/表/列类型（含长度）、nullable、server default；PK/UNIQUE/FK/CHECK 定义与
  FK 动作、constraint validity；索引列/唯一性/partial predicate；`legacy_migration` 函数签名+body+
  secdef+search_path；trigger 绑定表/事件/enabled。
- 反例在 `tests/test_b04_catalog_gate.py` 全部逐事务 rollback 并在结束时验证 clean gate 通过：
  EV03 三例（integer→bigint、drop `ck_webauthn_challenges_purpose`、disable `trg_lnm_guard`）
  ＋ default 变化、同名索引重定义、函数体变化、FK `ON DELETE` 动作变化、意外新增对象。
- `sql_owned.py` autogenerate allowlist 收紧为 schema+type+父表+对象名，且仅 reflected 且
  `compare_to is None`；`alembic check` 在迁移后仍 "No new upgrade operations detected"。
- CI：backend job 新增 "Schema drift gates (ORM + governed catalog)"（`alembic check` 与
  catalog gate 任一失败阻断）。

## B05a/B05b canonical AI 保存闭环（EV04 修复）

- 设计文档：[b05a-canonical-ai-creation.md](b05a-canonical-ai-creation.md)。
- 增量 schema：`alembic/versions/034_ai_run_provenance.py` + `models/ai_run.py`
  （`created_by` / `creation_context` / `confirmed_payload_hash` / `confirmed_at`，旧的 NULL 兼容）。
- 服务：`services/ai_creation_service.py`（构造 context、payload hash、`confirm_canonical_creation`
  统一锁序）。
- 路由：`/api/admin/mistakes/ai-candidate`、`/api/admin/mistakes/ai-confirm`。
- 收敛：`MistakeDraftCreate.source_run_id` 的旧可选绑定改为显式拒绝（无旁路）。
- 前端：`src/lib/api/mistakes.ts` 新增 candidate/confirm client；`mistake-draft-entry.tsx` 中作为
  可选"AI 错因候选"路径接入，来源（题目/答案/错因）变化即清除候选。
- 回归测试：`tests/test_b05_ai_canonical.py`（真实 ASGI+PG+隔离库+假 provider spy）：
  context 落库（含 source_question_id/version）→ 确认创建 draft 且运行绑定/哈希/accepted；
  错 actor 403；同 payload 重放返回原实体且 count=1；异 payload 409；题面版本 stale 409；
  双会话并发：同 payload 一个创建一个幂等，异 payload 一个创建一个 409。
- 迁移链：`astra_week4_rework` fresh `033 → 034 upgrade head`；`alembic check` 通过；
  catalog manifest 重生成至 revision 034；`main.EXPECTED_ALEMBIC_REVISION` 同步 034。

## B06 OCR 手工路径（EV05 修复）

- 产品代码：`capture-workspace.tsx` `DraftFieldsSection` —— `show` 加入 `uploaded` 项，标题
  "人工题面（可编辑）"（与 AI 草稿标题区分，避免把人工内容标记为 AI）；recognized-but-no-question
  时渲染"请继续在下方填写题面并保存"的引导。保存即走既有 PATCH → 服务端进入 ready → ConvertForm。
- 保留：识别/重试服务端 fail-closed；识别按钮仍只受 env 开关驱动；未启用时无 provider 调用。
- 回归：`capture-workspace.test.tsx` 新增 2 例 —— uploaded→填题面→保存（PATCH 断言含
  question_draft_text）→ready→转换表单可见；recognized-only 提示。

## B07 综合复验

见 [STATUS.md](STATUS.md)（本轮实测命令、覆盖和遗留未验收项）。
