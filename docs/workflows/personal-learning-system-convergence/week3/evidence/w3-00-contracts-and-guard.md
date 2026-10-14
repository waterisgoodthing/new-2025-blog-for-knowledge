# W3-00 实现报告 — 合同固化与 scratch 守卫 runner

- agent: W3-00-impl-contracts（profile=senior-backend-engineer，role=implementer）
- 日期: 2026-09-22
- 任务书: [../tasks/w3-00.md](../tasks/w3-00.md)（任务 1 + 任务 2，本 agent 只做这两件）
- 输入事实（未重复盘点）: `w3-00-inventory-legacy-mistake.md`、`w3-00-inventory-migration-adapter.md`、`w3-00-inventory-runtime-contracts.md`

---

## 1. Conclusion

`PASS` — 两件交付物均已落地并自证：

1. Week 3 合同（W3-D03/D04/D05/D06/D09）以纯断言/fixture 测试锁定于 `backend/tests/test_week3_contracts.py` + `backend/tests/week3_contracts_support.py`，32 个测试全绿。
2. scratch-only 守卫 runner 落地于 `scripts/week3-scratch-guard.py`，配套 13 个测试全绿；负向用例（blog_db / blog_v2 / prod URL / 空名 / 越界库名 / 非法字符）全部 FAIL 退出 1，`run` 在 FAIL 时不执行子命令。

未触碰 `backend/app/**`、`backend/alembic/**`、`src/**`、`package.json` 及任何既有 dirty 文件；未做 git add/checkout/stash/revert。

## 2. Changes

| 文件 | 动作 | 内容 |
| --- | --- | --- |
| `backend/tests/week3_contracts_support.py` | 新增 | 合同常量 + 纯函数（allowlist、visibility 映射、TypedDict 形状、排序键、零分母比率、键型常量、F-1～F-9 / K-1～K-12 集合） |
| `backend/tests/test_week3_contracts.py` | 新增 | 32 个可执行断言测试（见 §3） |
| `scripts/week3-scratch-guard.py` | 新增 | `check` / `run` 两子命令的 scratch 守卫 runner |
| `scripts/week3-scratch-guard.test.py` | 新增 | 13 个正/负向测试（unittest，可 `python3` 直跑或 `pytest` 指定路径） |
| `week3/evidence/tests/w3-00-contracts-pytest.txt` | 新增 | 合同测试输出 |
| `week3/evidence/tests/w3-00-scratch-guard-tests.txt` | 新增 | 守卫测试输出 |
| `week3/evidence/tests/w3-00-acceptance.txt` | 新增 | 验收命令全量输出（§4 表） |
| `week3/evidence/w3-00-contracts-and-guard.md` | 新增 | 本报告 |

## 3. 合同固化明细（任务 1）

### 3.1 W3-D03 公共 DTO allowlist

- `PUBLIC_MISTAKE_DTO_ALLOWLIST` 恰为 11 项：`id,title,question_text,correct_answer,analysis,reason_category,mistake_reason,difficulty,knowledge_point_ids,created_at,updated_at`。
- 拼写断言：`difficulty` ∈ allowlist，`difficult` ∉ allowlist。
- 排除断言：`my_answer,source_draft_item_id,subject_id,version,review_item_id,status,visibility` 均 ∉ allowlist（`PUBLIC_MISTAKE_DTO_FORBIDDEN` 另含 `question_id`）。
- 真实 schema 对照（防漂移）：`MistakeOut.model_fields`（`backend/app/schemas/mistake.py:84-103`，运行时读取）断言
  - `MistakeOut` 字段集 ≠ allowlist；
  - `MistakeOut` **包含**全部私有字段（`my_answer` 等 7 项）；
  - allowlist ⊆ `MistakeOut` 字段（公共字段必须在 admin DTO 中真实存在，不许凭空发明）。

### 3.2 W3-D06 visibility/status 映射矩阵

- 纯函数 `map_legacy_note_to_mistake_visibility(status, hidden) -> (canonical_status, visibility)`（support 模块，未改 `backend/app/**`）。
- 参数化 4 格断言（`LEGACY_NOTE_VISIBILITY_MATRIX`）：

| legacy status | hidden | canonical status | visibility |
| --- | --- | --- | --- |
| published | False | active | **public** |
| published | True | active | private |
| unpublished | False | active | private |
| unpublished | True | active | private |

- 附加断言：4 格恰覆盖 2×2 组合；`visibility='public'` 恰 1 格（published×hidden=False）；canonical status 恒 `active`（legacy 发布态不得混入学习生命周期）。

### 3.3 W3-D05 analytics / practice / dashboard 形状

| 合同 | 锁定内容 |
| --- | --- |
| KP analytics item | TypedDict `KPAnalyticsItem` = `knowledge_point_id` + 7 指标（`attempt_count,wrong_count,review_count,due_count,accuracy,wrong_rate,lapse_count`）；`KP_ANALYTICS_METRIC_FIELDS` 与 W3-D05 列表双向相等 |
| 排序键 | `KP_ANALYTICS_SORT_KEY == ("-wrong_rate","-lapse_count","-due_count","knowledge_point_id")`；`kp_weakness_sort_key` 实测：高 wrong_rate 优先 → 同率高 lapse_count 优先 → 同率高 due_count 优先 → 同率按 `knowledge_point_id` 升序（稳定决胜，含平局用例） |
| practice item | TypedDict `PracticeItem` 必有 `question_id,knowledge_point_id,selection_reason`（集合双向相等）；禁止 `answer_data,correct_answer,analysis,explanation`（与注解键不相交）；`assert_practice_item_keys` 校验器对缺失/泄漏均抛错 |
| practice response | TypedDict `PracticeResponse` 键集恰为 `{items, empty_metadata}`；`PRACTICE_ITEMS_MIN=0`、`PRACTICE_ITEMS_MAX=10` |
| dashboard summary 增量 | `DASHBOARD_SUMMARY_DELTA_FIELDS` 恰为 `{review_today_count,practice_today_count,weak_top3,recently_mastered_4,today_first_action}` |
| 零分母 | `compute_attempt_rates(0, 0) == (0.0, 0.0)`，二者为 `float`、非 `None`、非 NaN；非零分母另测（4 次 1 错 → 0.75/0.25） |

### 3.4 W3-D04 migration 032 键型

- 合同常量：`NOTE_ID_TYPE="UUID"`、`KNOWLEDGE_POINT_ID_TYPE="INTEGER"`。
- 真实模型核对（运行时读 SQLAlchemy column type，非抄写）：
  - `app.models.note.Note.id` → `UUID`
  - `app.models.taxonomy.KnowledgePoint.id` → `INTEGER`
  - `app.models.question.QuestionKnowledgePoint.knowledge_point_id` → `INTEGER`、`question_id` → `UUID`
- 反回潮断言：`KnowledgePoint.id` 与 `QuestionKnowledgePoint.knowledge_point_id` 均 ≠ `UUID`（防 D8 UUID 草图回潮）。

### 3.5 W3-D09 legacy 冻结目标清单

- `LEGACY_MISTAKE_WRITE_FREEZE_TARGETS` 恰为 9 项（F-1～F-9）：`notes.create_mistake_type, notes.update_type_to_mistake, notes.promote, ui.staged_mistake_form, ui.mistake_form, ui.write_note_mistake_edit, review.sm2_submit, notes.field_update_mistake, notes.delete_mistake`；与期望集合双向相等 + `len==9`。
- `LEGACY_MISTAKE_COMPAT_READS` 恰为 12 项（K-1～K-12）：`k1.notes.list, k2.notes.get_by_slug, k3.review.queue, k4.review.stats, k5.review.plan, k6.hooks.use_note_index, k7.ui.public_mistakes_page, k8.ui.note_detail_mistake_render, k9.services.knowledge_suggestion_reads, k10.search.notes_search, k11.ui.list_sidebar_route_metadata, k12.tests.compat_baseline`；`len==12`。
- 附加断言：冻结集与兼容读集不相交（F 与 K 无重叠）。

## 4. 守卫 runner 明细（任务 2）

`scripts/week3-scratch-guard.py`：

- allowlist 正则 `^astra_week3_[a-z0-9_]+$`（后缀至少 1 个 `[a-z0-9_]` 字符）。
- 拒绝顺序：URL 含 `blog_db`/`blog_v2` 子串 → 库名含该子串 → 空名 → 正则不匹配。均 FAIL 退出 1。
- `.env` 启发式防护：无 `--db-name`/`--url` 时读环境变量 `DATABASE_URL`；其库名不在 allowlist 即拒绝（错误信息注明来源 `env:DATABASE_URL`）。显式参数路径 `--db-name` / `--url` 为受控通道。
- 子命令：`check`（只校验，打印 PASS/FAIL，退出 0/1）与 `run -- <command...>`（校验通过才以 `subprocess` 执行子命令并注入 `DATABASE_URL`；失败打印 `child command NOT executed` 且退出 1）。
- 仅 `--db-name` 时子进程 `DATABASE_URL` 构造为本地 scratch DSN `postgresql+asyncpg://localhost:5432/<db_name>`（不隐式继承生产 host/凭证；需他址时显式 `--url`）。

### 4.1 验收命令结果

| # | 命令 | 期望 | 实际 | 退出码 |
| --- | --- | --- | --- | --- |
| 1 | `PYTHONPATH=. .venv/bin/python -m pytest tests/test_week3_contracts.py -q`（自 `backend/`） | 全绿 | `32 passed in 0.16s` | 0 |
| 2 | `check --db-name astra_week3_demo` | PASS | `PASS: db_name='astra_week3_demo' source=explicit:--db-name` | 0 |
| 3a | `check --db-name blog_db` | FAIL | `database name contains forbidden substring 'blog_db'` | 1 |
| 3b | `check --db-name blog_v2` | FAIL | `database name contains forbidden substring 'blog_v2'` | 1 |
| 3c | `check --db-name astra_week2_x` | FAIL | `does not match allowlist` | 1 |
| 3d | `check --db-name ''` | FAIL | `empty database name` | 1 |
| 3e | `check`（`DATABASE_URL=...blog_v2`，模拟 `.env` 默认） | FAIL | `URL contains forbidden substring 'blog_v2' (source=env:DATABASE_URL)` | 1 |
| 3f | `check --url .../production_db`（prod URL） | FAIL | `does not match allowlist` | 1 |
| 4a | `run --db-name blog_db -- echo SHOULD_NOT_RUN` | 不执行子命令 | 输出含 `child command NOT executed`，**无** `SHOULD_NOT_RUN` | 1 |
| 4b | `run --url .../blog_v2 -- echo SHOULD_NOT_RUN` | 不执行子命令 | 同上 | 1 |
| 4c | `run --db-name astra_week3_demo -- python3 -c ...` | 执行子命令 | `CHILD_RAN postgresql+asyncpg://localhost:5432/astra_week3_demo` | 0 |
| 5 | `python3 scripts/week3-scratch-guard.test.py` | 全绿 | `Ran 13 tests ... OK` | 0 |

补充负测（守卫测试内覆盖）：`astra_week2_x`、`astra_week3_bad-name`、`astra_week3_bad.name`、`astra_week3_bad!`、`astra_week3_UPPER`、`ASTRA_WEEK3_X`、`astra_week3`（空后缀）、`week3_demo`、`production_db` 均 FAIL；`astra_week3_demo` / `astra_week3_x` / `astra_week3_pr09` / `astra_week3_ok_01` 与 `--url .../astra_week3_demo` 均 PASS；URL 子串污染（query 含 `blog_db`）亦 FAIL。

## 5. Evidence

- `evidence/tests/w3-00-contracts-pytest.txt` — 32 passed。
- `evidence/tests/w3-00-scratch-guard-tests.txt` — 13 tests OK（含逐用例诊断行）。
- `evidence/tests/w3-00-acceptance.txt` — §4.1 全量命令 stdout/stderr 与退出码。
- 真实 schema/模型核对发生在测试运行时（`MistakeOut.model_fields`、`Note.__table__.c.id.type` 等），非文本抄写，可随模型漂移自动变红。

## 6. Verification

| 手段 | 结果 |
| --- | --- |
| `cd backend && PYTHONPATH=. .venv/bin/python -m pytest tests/test_week3_contracts.py -q` | `PASS`（32 passed） |
| `python3 scripts/week3-scratch-guard.test.py` | `PASS`（13 tests OK） |
| runner 正/负向命令（§4.1） | `PASS`（期望与实际逐条一致） |
| `git status --short` 对照 | `PASS`（本 agent 新增 4 个代码文件 + evidence；未修改/未 stage 任何既有文件） |
| 越界写入检查 | `PASS`（`backend/app/**`、`backend/alembic/**`、`src/**`、`package.json` 零改动） |

最终状态：`PASS`。

## 7. Risks / Remaining

- W3F-11（live `alembic current` 钉扎）**未执行**：本任务只产出守卫 runner，不在数据库上跑 alembic。留待 PR-09 在 `astra_week3_*` scratch 上以本 runner 执行 `alembic current` 复核 head=030（与 inv-runtime 的 offline 单头证据互补）。
- practice response 的 `empty_metadata` 只锁**字段存在**（键集 `{items, empty_metadata}`），未锁其内部键名（任务书未给出）；PR-13 可在不改本合同的前提下定义内部结构。若需锁定内部键，请在 PR-13 任务书中补定。
- KP analytics item 含 `knowledge_point_id`（排序决胜所需），指标 7 项与 W3-D05 列表严格相等；若 PR-10 需展示 `name` 等派生字段，属扩展而非违约，但应回写本合同。
- `run` 在仅 `--db-name` 时用本地 scratch DSN 模板（不含凭证）；需要凭证/host 时必须显式 `--url`。这是刻意保守取舍，已在脚本 docstring 声明。

## 8. unresolved_issues

无阻塞项。待主 agent 裁决（非本任务范围）：

1. `empty_metadata` 内部键名是否要在 PR-13 前补锁（见 §7）。
2. W3F-11 的 live alembic 钉扎执行时机（建议 PR-09 首个 scratch 动作，经本 runner）。
