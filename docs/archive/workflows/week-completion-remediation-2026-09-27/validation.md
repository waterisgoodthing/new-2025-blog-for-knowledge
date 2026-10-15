# 验证计划与证据状态

审计E01–E13是2026-09-27已有证据：前端522、后端922/9skip、Chromium5、构建/隔离PG。本轮引用而未复跑，仅核对源码和方案。实施环境为Node24、backend/.venv、PG16新建本地隔离库；DB命令先经现有guard，不连接默认/生产库，不输出凭据。

## 验收矩阵

| ID | 实验/反例 | 必须验证的结果 |
|---|---|---|
| V01 / F01 | 真浏览器A+C、C+A、取消、少选/多选/空集；单选/判断/短答/人工判定代表题；提交后改答案/竞争请求 | 请求为稳定集合；正确集合为correct，少选/多选为incorrect，空集禁止提交，人工题needs_human；只在用户确认后写ReviewRecord且绑定本次Attempt/item；rating0–5保留；失败不重复推进 |
| V02 / F02 | Question两个KP→错答→draft→确认→Mistake→错再答rating0→再次正确；显式[]/人工替换/无KP/非法学科/重复确认/Question后改KP | 分别读QuestionKnowledgePoint与draft/mistake的KnowledgePointLink；review_count+1，rating<=2时lapse+1；due按受控时钟及新计划确定，通常提交后减少，不能断言全部指标+1；practice计数排除review context；Dashboard/Practice与事实一致 |
| V03 / F03 | move/add_tag/所有写入口清单；普通Note和legacy混合目标位于首/尾；匿名/管理员；canonical正例 | 管理员碰legacy返回410/code，整批无Note/Tag/Folder关联副作用；匿名按原认证拒绝；普通写成功、公开过滤与legacy兼容读保留 |
| V04 / F04 | fresh升级、空033→027→033、live challenge降级拒绝；分别破坏ORM与SQL-owned列/索引/CHECK | alembic check和catalog gate无未解释差异；真漂移反例失败；ledger/约束保留；不跨026不可逆边界，不删challenge凑绿 |
| V05 / F05 | 真实canonical生成返回run_id→人工保存；随机/错task/失败/拒绝run、错来源/版本、同目标重复、异目标冲突、并发、保存失败、run记录不可用 | AiRun与实体关联同次提交；失败无半完成；同目标幂等、异目标拒绝；Capture target不变；弃用NULL合法；不静默保存无来源内容 |
| V06 / D06 | 禁用时UI/直连识别及重试API、手工转换；或授权后的固定10真实样本 | 禁用时provider调用为0且手工流程可完成；真实评估有样本hash/字段评分/成本/耗时，pipeline完成至少8/10（不等于字段准确率80%，字段质量标准在R00冻结），未达标禁用；mock不能证明质量 |
| V07 / D12 | Question→Attempt→Draft→Mistake→ReviewRecord→KP→Dashboard/Practice；题型、错/对/人工/空关联/冲突代表矩阵 | 每条不变量有fixture、测试ID、失败证据与修复证据；不mock核心service逃避真实写链，无需盲做全笛卡尔积 |

V02用受控时间和到期fixture，不等待多天或改生产时间。提交后使用新事务/请求回读，避免仅检查session缓存。Playwright用真实cookie会话；截图/trace辅助，不替代持久化断言。

## 检查层次

1. 每项先固化失败复现（审计probe复核后可复用），再跑目标组件/service/HTTP/隔离PG测试；UI行为须有真实浏览器。
2. R07执行 `npm test`、`npx tsc --noEmit`、`npm run test:typecheck`、`npm run build`、`npm run build:cf`；backend目录经guard注入安全环境后执行 `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q -rs`。迁移/drift使用同一隔离实例。
3. 依当前CI、playwright.config.ts与docs/ci-local-reproduction.md核对启动/seed配置后，运行同源workerd/后端的 `npm run smoke` 和 `npm run test:e2e`；不直接复制文档默认DB连接。
4. 逐V项报告、解释skip/warnings；不硬编码旧测试数量为验收线。有修改重跑受影响项，最后证据绑定最终快照；无变化不机械重跑全套。
5. 真实OCR、远端CI、生产状态单列，不能借本地通过填PASS。

## 本轮检查记录

- 只读核对F01–F05，不重新裁决所有Week Gate。
- 文档检查：五份核心文件、相对链接、REQ/R/V映射、whitespace与基线文件哈希。
- 独立reviewer：`/root/plan_review`，无写入/实施所有权；最终结论PASS_WITH_NOTES，无阻断；两项措辞意见（V01正负例与OCR完成率定义）已采纳。
- 业务修复与运行回归：NOT_VERIFIED；实施：NOT_AUTHORIZED。

文档验收：PASS。5份核心文档相对链接检查无断链；新增文件git diff --no-index --check无空白错误诊断（退出1表示存在新增diff）；2,872份既有文件SHA-256比对未变。主Agent接受方案交付，非业务代码或发布accept。独立审阅仅静态，F05真实入口与绑定仍须R00专业门禁。

## R00–R07 本地实施检查记录（2026-09-27）

环境：Node v26、backend/.venv (Py3.12)、本地 PG16 隔离库 `astra_week4_r00r07*`（经 `scripts/week4-scratch-guard.py` 注入 `DATABASE_URL`）。未连接默认/生产库，未输出凭据。

| 检查 | 命令 | 结果 |
|---|---|---|
| 基线完整性 | 复算 `baseline-files.json` 2872 项 | 0 缺失；27 项变化均为本轮有意修改 |
| 后端回归 | `pytest tests/ -q`（fresh `astra_week4_r00r07_full`） | 940 passed, 9 skipped, 47 subtests；skip 均为既有 `LSR03_DATABASE_URL`/scratch-only |
| 迁移漂移（已有库） | `alembic check`（`astra_week4_r00r07`） | No new upgrade operations detected |
| 迁移漂移（fresh） | `alembic upgrade head` + `alembic check`（`astra_week4_r00r07_fresh`） | No new upgrade operations detected |
| 前端单测 | `npm test` | 525 passed (70 files) |
| 前端类型 | `npx tsc --noEmit` / `npm run test:typecheck` | 退出 0 |
| 前端构建 | `NEXT_PUBLIC_API_URL=http://ci-check.invalid:8000 npm run build` | 退出 0 |
| CF 构建 | `NEXT_PUBLIC_API_URL=http://ci-check.invalid:8001 npm run build:cf` | OpenNext build complete |
| F03 冻结 | `tests/test_f03_freeze_coverage.py` | 1 passed（真实 ASGI handler + PG 元数据写入） |
| F04 schema | `tests/test_f04_schema_ownership.py` | 4 passed（含删 SQL-owned/ORM 索引的反例） |
| F05 绑定 | `tests/test_ai_governance.py` | 20 passed（含 failed/rejected/异目标/幂等/非创建型反例） |
| F01/F02 | `review-queue.test.tsx`, `test_attempt_service.py` | 6 passed / 4 passed |

### D12 穿链代表样本索引

| 不变量 | 代表样本 | 测试位置 |
|---|---|---|
| F01 多选集合、编辑失效、空集禁止提交 | `multiple_choice` A+C 提交 `A,C`；变更答案清除评价 | `review-queue.test.tsx` |
| F02 Question→Attempt→Draft→Mistake KP 继承 | 2 KP 多选题错答→草稿→转换 → Mistake 同 KP | `test_attempt_service.py::test_kp_chain_from_attempt_to_review_analytics`、`test_auto_draft_snapshots_question_knowledge_points_into_mistake` |
| F02 Review→KP 指标（review 计数/lapse；practice 排除 review context） | rating 0 后 `review_count=1`、`lapse_count=1`、`attempt_count=1`（review 再答不计入 practice） | 同上 |
| F03 legacy mistake 元数据冻结 | suggestions move/add_tag、folder move/delete、tag merge/delete、Note↔KP link 均 410 且无副作用；普通 Note 成功 | `test_f03_freeze_coverage.py` |
| F04 schema authority | 双门禁 + 删索引可检测 | `test_f04_schema_ownership.py` |
| F05 生成→run_id→保存绑定 | gateway 返回 `run_id`；canonical MistakeDraft 保存携带 `source_run_id` 原子绑定 | `test_ai_governance.py::GatewayRunIdTest`、`CreationTypeSaveBindingTest` |
| F06/D06 OCR 出口 | 默认禁用不触发 provider，手工路径可完成 | `test_capture_service.py::test_recognition_disabled_by_default_never_calls_provider`、`capture-workspace.test.tsx` |

### 未覆盖 / 未验证

- 真实 OCR provider 10 样本评估：**NOT_VERIFIED**（本轮走禁用策略，未外发）。
- 远端 CI、生产 cookie/CORS、真实设备 passkey、生产迁移/恢复、历史回填：**NOT_VERIFIED / NOT_AUTHORIZED**。
- 前端仅 jsdom 渲染断言；真实浏览器 E2E 未在本轮运行（`npm run test:e2e` 需同一构建的全栈环境）。
