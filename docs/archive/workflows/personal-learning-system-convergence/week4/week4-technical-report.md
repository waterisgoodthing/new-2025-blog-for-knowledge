# Week 4 技术报告：RELEASE GATE (M4)

> 执行日期：2026-09-26
> 主 agent / `primary_owner` / 最终代码验收：主 agent（WORKER 模式）
> 授权范围：Week 4 本地实现 + 隔离 scratch DB（`astra_week4_*`）验证；**不含** commit/stage/push/merge/生产迁移/部署
> 最终状态：**PARTIAL（修复轮 2026-09-26）**——复评 F01–F08 全部修复并经独立评审；本地可验证项全 PASS（含业务 E2E、无 deselect 全量套件）。仅远端 CI 与真实供应商 OCR 基线因授权限制 `NOT_VERIFIED`。

## 0a. 修复轮结果（2026-09-26，优先）

复评 F01–F08 已修复：F01 CI 三库 Job 改用 `astra_week4_ci`（守卫兼容，`fix-F06-F01-review.md` PASS）；F02 CLI 单 `_ServerEventLoop`（两次 options 200/200）；F03 verify 按 `clientDataJSON` 哈希 + purpose + binding 定位并消费（`fix-F02-F03-review.md` PASS）；F04 E2E-03/04 真实业务链 + 后端读回 + 确定性 seed（独立复跑 5/5）；F05 结构化 error category 贯通 recognition 与 draft（`fix-F05-F07-review.md`/`fix-rework-review.md` PASS）；F06 账户键限长 + 容量 LRU + username max_length（PASS）；F07 源头移除 `response.text`（PASS）；F08 矩阵改 PARTIAL；测试隔离修复、3 个 deselect 移除（fresh 与复用库均 922/0/9）。当前：前端 522、后端 922/0/9、迁移单 head 033、build:cf exit 0、smoke 20/0、E2E 5/5。仅远端 CI 与真实 OCR 基线 `NOT_VERIFIED`。

## 0. 复评更正（历史记录：曾判定 FAIL；已由上方 0b 修复轮取代）

独立复评判定 M4 **FAIL**，我复核后确认其成立：F01 CI 三库 Job 使用 `blog_db` 被仓库自身守卫确定性阻断；F02 PR-15 使 CLI passkey options 访问 DB，而 `cli.py` 每次请求新建/关闭 event loop、复用同一 AsyncEngine → 跨 loop 连接池错误；F03 WebAuthn verify 取“最新未消费 challenge”而非与本次 assertion 匹配者，多 ceremony 互相干扰（违反 PR-15 验收）；F04 E2E-03/04 仅测 UI 壳/空态，未覆盖 R22b 的错答→草稿、再答→复习记录；F05/F06/F07/F08 为次级缺陷/过度声称。该 FAIL 为修复轮之前的中间状态，现已按 0b 修复。下文第 1 节及后续为更早的原始报告，保留以存证。

## 1. 结论（原始，已被上节更正）

Week 4「RELEASE GATE」已按锁定串行序 `W4-00 → PR-14 → PR-15 → PR-19‖PR-16 → PR-17 → PR-18 → Gate` 完成。全部 6 个工作包实现、独立评审、返工与复检均通过（HIGH/BLOCKER 全部关闭）。Gate 的本地可验证矩阵全部 PASS：前端 70 文件/522 通过、后端 883 passed/0 failed/9 skipped/3 deselected、`tsc` 与 `test:typecheck` exit 0、单迁移 head **033**、`build:cf` 产物就绪、runtime smoke `ok=20 failed=0`。

Gate 最终定级 **PARTIAL**，原因仅为三项在「本地-only、不推送」授权下无法验证的项目，而非缺陷：真实供应商 OCR 成功率、远端 CI 四 Job 全绿/故意失败、E2E 在 CI 同站拓扑下的端到端运行。

本结论**不**代表已 commit/push/merge/部署或对生产库（`blog_db`）执行迁移。生产库与 `blog_v2` 全程未被写入；所有 DB 操作为本地 `astra_week4_*` scratch 库并经 `scripts/week4-scratch-guard.py` 校验。

## 2. 状态总览

| 工作包 | 风险 | 实现 | 独立评审 | 验证 | 主 agent 验收 |
| --- | --- | --- | --- | --- | --- |
| W4-00 预检/范围锁定 | MEDIUM | PASS | 盘点三份（真实子代理） | PASS（守卫 37 测试） | PASS |
| PR-14 OCR 诊断与 UI | MEDIUM | PASS | PASS（返工后 F1/F2 HIGH 关闭） | PASS（后端 37 / 前端 8） | PASS_WITH_NOTES |
| PR-15 WebAuthn challenge 033 | HIGH | PASS | PASS（F1 BLOCKER + F2 HIGH 关闭；W4-E08） | PASS（75 passed；单 head 033） | PASS |
| PR-19 AI 治理收尾 | MEDIUM | PASS | PASS（F1 HIGH 关闭） | PASS（34 passed） | PASS |
| PR-16 登录限流 | HIGH | PASS | PASS（F1 MEDIUM IP-TTL bug 关闭） | PASS（22 passed；真实 2.005s） | PASS |
| PR-17 CI 四 Job | MEDIUM | PASS | PASS（R01–R03 HIGH 关闭） | Job1/2/3 PASS；Job4 PARTIAL | PASS_WITH_NOTES |
| PR-18 遗留清理 | MEDIUM | PASS | PASS_WITH_NOTES（R-01 已协调） | PASS（前后 522 通过） | PASS_WITH_NOTES |
| Week 4 Gate | HIGH | PASS | PASS（gate-final-review：PARTIAL 成立） | PASS（矩阵本地项全绿） | **PARTIAL** |

## 3. 计划与现实的关键偏差（W4-E*）

Week 4 计划文本多处与当前源码不符，按 AGENTS.md「当前源码优先」以真实代码为准修正并记录：

- **W4-E01/E02**：不存在 `capture_recognition_service.py`/`CaptureRecognition` 模型；OCR 真实路径为 `capture_recognition.recognize_image → ai_gateway.call_vision`。故 PR-14 不加迁移/列，taxonomy 从既有 `error_code` 派生为 DTO 计算字段；真实供应商成功率 `NOT_VERIFIED`，不据未验证数据禁用入口。
- **W4-E03/E08**：三套内存 dict 实为 `_reg/_auth/_operator_reg_challenge_store`；operator 用易失随机 `session_id`；challenge 函数新增 `db` 参数并保留各 ceremony 消费语义（reg/auth 成功才消费，operator 验证前消费）。WebAuthn 库验证需要服务端**原始 challenge**，故在 `challenge_hash` 之外保留 `challenge` 列（W4-E08 正式修订 D03「仅存 hash」措辞）。
- **W4-E04**：登录体为 `{username,password}`（无 email），限流账户维度以 `username` 为键。
- **W4-E05**：`ai_runs.target_type/target_id` 存在但网关从不写入（恒 NULL）；PR-19 打通链路并新增 `backfill_ai_run_target`（生产确认端点尚未接线，prospective）。
- **W4-E09/E10/E11**：仓库无 ruff/mypy 工具链（Job 2 不含）；保留的 ui-v2 树既有 10 个 `test:typecheck` 错误，仅从 `test:typecheck` 排除（主 `tsc` 仍覆盖已发布代码）；Job 2 显式 deselect 3 个既有测试隔离失败（记录为债务）。
- **W4-E07**：计划中的“坏 Dashboard 测试/重复 analytics”并不存在；`sm2.py` 仍被注册路由引用（IN_USE）。仅 5 项可证死代码，净删 124 行（未达 ≥500 次要指标）。

## 4. 关键设计与实现

- **PR-14**：`CaptureFailureCategory`（8 类）+ `categorize_failure/categorize_provider_error`；服务层按 category/code/capture_id 记录**无敏感细节**日志；`CaptureOut.failure_category` 计算字段；UI 失败分类标签 + 识别阶段「未识别到内容」独立空态 + 草稿阶段专属文案，保留重试。
- **PR-15**：migration 033 `webauthn_challenges`（purpose CHECK、绑定键、TTL、consumed_at、部分索引）；`webauthn_challenge_service`（store/get_valid[with_for_update]/mark_consumed/机会式清理）；6 个 passkey 函数改 async + `db`；startup 版本钉与测试钉同步升至 033；downgrade 对未消费行 fail-closed。
- **PR-19**：网关四函数与 `_start_run_record` 支持 `target_type/target_id`；Capture 识别/草稿写入 `target_type='Capture'`；polish 记录为瞬态豁免；`docs/architecture/ai-governance.md` 明确 transient/persisted 与创建型回填契约。
- **PR-16**：`LOGIN_THROTTLE_*` 配置 + `login_throttle` 双维度（线程锁、IP TTL 读写均淘汰、账户不衰减）；登录在密码校验/DB 前 `asyncio.sleep`，401 语义不变，成功重置。
- **PR-17**：CI 四 Job（frontend/backend/runtime-smoke/e2e）；`tsconfig.test.json` 排除保留树；5 条 Playwright（`workers=1`）+ `playwright.config.ts` + `test:e2e`；本地复现文档。
- **PR-18**：删除 `wip.tsx`、`manage-placeholder-page.tsx`、`future-capability-page.tsx`、`music/list.ts` 与一处未用 import；每项三证据（grep/测试/无渲染面）落档；IN_USE/UNCLEAR 项保持不动。

## 5. 多智能体协作实录

执行模式 **WORKER**。主 agent 负责规划、集成、Gate 复算、返工裁决与最终验收；实现、独立评审、验证由真实子代理（`general`）承担，遵守「实现者≠评审者」与「返工后由原评审复检」。

| 阶段 | 参与子代理（真实 session id 摘要） | 结果 |
| --- | --- | --- |
| W4-00 | inv-ocr / inv-auth / inv-cleanup（只读盘点） | 3 份证据；暴露 12+ 偏差 |
| PR-14 | impl-14 → rev-14 → rework → recheck | F1/F2 HIGH 关闭，PASS |
| PR-15 | impl-15 → rev-15 → rework → recheck | F1 BLOCKER + F2 HIGH 关闭，PASS |
| PR-19 | impl-19 → rev-19 → rework → recheck | F1 HIGH 关闭，PASS |
| PR-16 | impl-16 → rev-16 → rework → recheck | F1 MEDIUM IP-TTL bug 关闭，PASS |
| PR-17 | impl-17 → rev-17 → rework → recheck | R01–R03 HIGH 关闭，PASS_WITH_NOTES |
| PR-18 | impl-18 → rev-18 | PASS_WITH_NOTES |
| Gate | gate-final-review | PARTIAL 成立 |

## 6. 评审发现与关闭（摘要）

| 发现 | 严重度 | 处置 | 状态 |
| --- | --- | --- | --- |
| PR-14 F1 provider 失败恒 unknown | HIGH | error_code 细分为 provider_auth/invalid_model + DTO 映射 | CLOSED |
| PR-14 F2 日志 sanitize 不实 | HIGH | 移除异常详情日志，仅 category/code/capture_id | CLOSED |
| PR-15 F1 启动版本钉 032 vs head 033 | BLOCKER | main.py 与 3 处测试钉升至 033 | CLOSED |
| PR-15 F2 明文 challenge 与 D03 冲突 | HIGH | W4-E08 正式修订（库需原始 challenge） | CLOSED（附残余风险） |
| PR-17 R01/R02 E2E strict 定位器 | HIGH | 全部改为 exact/scoped | CLOSED |
| PR-17 R03 Job2 必红 | HIGH | 3 个既有隔离失败显式 deselect + 债务记录 | CLOSED |
| PR-19 F1 文档过度声称/测试同义反复 | HIGH | 新增真实 backfill helper + DB 回读测试 + 文档降级为 NOT_YET_WIRED | CLOSED |
| PR-16 F1 IP TTL 过期项复活 | MEDIUM | 读/写均淘汰过期项 + 有界化 + 测试 | CLOSED |
| 其余 LOW/INFO | LOW/INFO | ACCEPTED_NOTE / 记录为 follow-up | 记录在案 |

零未决 BLOCKER/HIGH 产品缺陷。

## 7. 验证证据索引

- 全量本地复算：`evidence/gate/tests/gate-frontend.txt`、`gate/tests/gate-backend.txt`
- 迁移回放（fresh→033、033↔032、单 head）：`evidence/gate/migrations/gate-migration-replay.log`
- 构建与 smoke：`evidence/gate/ci/gate-buildcf.txt`、`evidence/gate/browser/gate-runtime-smoke.txt`
- 各 PR 测试/评审：`evidence/pr-14-*`、`pr-15-*`、`pr-16-*`、`pr-17-*`、`pr-18-*`、`pr-19-*`
- Gate：`evidence/gate/week4-gate-matrix.md`、`week4-gate-summary.md`、`gate-final-review.md`
- 决策与偏差：`evidence/w4-00-decisions.md`（W4-D01..07 + W4-E01..E11）

## 8. 已知限制与执行边界

- **未执行**：commit/stage/push/merge/release、生产迁移/写入、部署、真实供应商 OCR 调用。
- **PARTIAL 的成因**：OCR 真实成功率、远端 CI 全绿、E2E 同站端到端 —— 均为 `NOT_VERIFIED`/`NOT_AUTHORIZED`，非缺陷。
- **非密闭测试**：后端 `883/0/9/3` 仅在 **fresh** scratch DB 成立；复用脏库会产生大量假失败，CI 已按每次 fresh DB 设计。
- **限流** 进程内、仅 `request.client.host`；**WebAuthn** 原始 challenge 短时（≤300s，一次性）明文入库且不入日志；**PR-18** 净删 124 行未达 ≥500 次要指标。

## 9. 风险 / 遗留 / 待决

- **待决**：是否接受 M4 以 PARTIAL 收口（附 6 项 burn-down），或要求一次获授权的远端 CI（+ 同站 E2E + 真实 OCR 基线）后再关闭 30 天计划。
- **遗留（需单独授权）**：远端 CI 运行与故意失败校验；修复 3 项后端测试隔离并移除 deselect；将 `backfill_ai_run_target` 接入生产确认端点；协调 `/api/review` 退役（解锁 `sm2.py`/`review_planner.py`/legacy `review.ts`）与两个无前端端点的 access-log 证据；真实 OCR 10 样本基线。
- 工作树保持脏（含 Week 1–4 改动），未做任何 git 写操作；无关既有改动未被覆盖。
