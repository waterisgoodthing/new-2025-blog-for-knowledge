# Week 4 代码质量与功能复验

日期：2026-09-26。**评估已完成；M4 RELEASE GATE：FAIL。**

当前结果不支持“所有本地可验证项 PASS，仅剩授权限制”的判断。基础测试和正常页面流程通过，但发现可复现的认证功能缺陷、CI 配置阻断和业务 E2E 覆盖缺口。建议先修复再验收，不能仅附 burn-down 就按原标准关闭 M4。

## 范围、依据与独立分工

需求来源：本次用户要求对 Week 4 做代码质量评估和功能验证。依据：Week 4 README、各 PR 任务、TRACKING 的执行决策、上级 requirements R22b，以及当前源码。记忆仅用于定位治理原则，所有具体结论均由当前材料核对。

执行模式 WORKER，主代理为 primary_owner。真实独立角色：`auth_review` 审查 PR-15/16；`capture_ai_review` 审查 PR-14/19 并复核 R22b；`backend_verify` 独立执行数据库、后端测试和 CLI 复现；主代理审查 PR-17/18、复验前端/构建/浏览器并交叉核对证据。无人实现或修复产品代码。

任务顺序：范围核对 → 独立只读审查与隔离验证 → 缺陷证据交叉核对 → 本报告与后续验收要求。独立验证并行不改变原实施串行 Gate。

环境：macOS，本地 PostgreSQL / Python 3.12；构建和 Playwright 使用 Node 24.18.0。工作树 HEAD `4a954eaa92952fcc5a6b18a2e15d2e824b094e41`，混有多周未提交修改，不能将全部 HEAD diff 归属 Week 4。本次保留原文件，仅新增报告和证据。

## 发现（按影响排序）

### F01 — HIGH：CI 三个数据库 Job 会被自身安全守卫拒绝

位置：`.github/workflows/ci.yml:50,119,217` 及对应服务 `POSTGRES_DB`；`backend/alembic/env.py:58`；`backend/app/utils/scratch_db_safety.py:16,73`。

三个 Job 都使用 `blog_db`。迁移在连接前要求本地 `astra_week3_*` / `astra_week4_*`，或独立批准的精确目标；CI 没有后者。pytest 连接守卫也无 CI 豁免，拒绝 `blog_db`。纯函数复现已确认拒绝，无需访问或写入受保护数据库。

因此远端尚未执行不只是证据缺失：当前配置存在可确定阻断。此前本地复现使用 scratch 库，改变了关键变量，不能作为原样 CI 通过证明。修复应统一 CI 服务库名、URL 与 health check 为受允许的测试库，不应放松保护真实库的安全规则。

### F02 — HIGH：PR-15 使 CLI Passkey 注册发生跨事件循环连接池错误

位置：`backend/app/cli.py:158-173,181-182,206-212,237-241`。

HTTP handler 共用一个 AsyncEngine，每次调用却新建并关闭 event loop。PR-15 将 options/verify 改为访问数据库后，连接池保留上一 loop 的 asyncpg 连接。独占 PostgreSQL scratch 库中运行真实 `create_registration_server`，连续两个 options HTTP 请求：第一次 200，第二次断连；trace 出现 `Future attached to a different loop`，随后有 `another operation is in progress`。

影响：刷新/重试注册 options 即可触发，正常 options→verify 同样跨越此错误边界。没有进行真实设备注册；证据足以确认注册服务器请求生命周期回归。修复需让 engine/session 与 loop 生命周期一致，并通过真实 HTTP options→verify/重试测试，不只 mock service。

### F03 — HIGH：WebAuthn 多个登录 ceremony 仍互相干扰

位置：`backend/app/services/webauthn_challenge_service.py:100-103`；`backend/app/services/passkey_service.py:239-246`。

查询按 purpose/binding 选择最新未消费记录，而未定位本次 assertion 的 challenge。采用真实 ES256 签名、真实 WebAuthn verifier、SQLite 内存执行服务生成的查询进行确定性复现：A 独立验证成功；新增 B 后同一合法 A 返回失败；B 消费成功后 A 才重新成功。匿名 auth-options 请求也能发起 B。

这是 W4-E03 保留 latest 行为与“并发 ceremony 不互相覆盖/干扰”的验收冲突，不是声称代码偏离 W4-E03。表里能同时保留两行不等于两个 ceremony 均可完成。现有 lifecycle 的 concurrent 测试只验证插入和计数，未覆盖真实 assertion 匹配；本探针不证明 PostgreSQL 行锁并发正确性。另一个 PostgreSQL 双session消费探针返回 `[True, False]`，证明同一条记录只能消费一次；这与各自持有不同challenge的A/B匹配失败是两个独立问题。

### F04 — HIGH：两条关键 E2E 的业务内容被替换

位置：`tests/e2e/03-capture.spec.ts:22-37`；`tests/e2e/04-review-flow.spec.ts:23-32`。需求来源：上级 `requirements.md:232-233`。

约定分别是 question→wrong attempt→mistake draft 和 mistake→review→re-answer→review record；实际仅切换采集 tab、检查复习评分组或空态。本次这两个测试确实在真实浏览器通过，但未创建/断言错答、草稿、再答或复习记录。

历史 `pr-17-ci-run-local.txt:130-134` 说明因缺 seed 改用 data-independent 测试；没有找到批准替换 R22b 业务验收的决策。需确定性业务 seed 和真实页面操作/后端读回，否则即使 CI 全绿也不能宣称关键闭环 E2E 完整。

### F05 — MEDIUM：OCR taxonomy 未覆盖真实底层异常包装

位置：`backend/app/services/capture_recognition.py:95-99,142-145`；`capture_failure_taxonomy.py:63-76`；上游 `ai_service.py:139-140,200-213`。

仅 mock provider I/O 和数据库 writer，执行真实 recognition→gateway→fallback→parser：原生空消息 `httpx.ReadTimeout`、provider 返回非 JSON，两者最终都成为 `provider_error/unknown`，而不是 provider_timeout/invalid_response。原测试从 call_vision 边界人为抛有特定文案的异常，绕开了真实包装链。

底层信息丢失既有，新 taxonomy 未适配它是 Week 4 集成缺口。修复需保留稳定错误类别并增加上述跨层测试；不需要真实供应商即可复验。

### F06 — MEDIUM：不存在账户可造成限流字典持续增长

位置：`backend/app/services/login_throttle.py:119-125`；`backend/app/routers/auth.py:199-201`；`backend/app/schemas/auth.py:7-9`。

账户字典没有淘汰/容量上限，username 无长度约束，认证失败的不存在账户名也被永久保存。真实 login 路由配 fake no-user DB：三个约 100KB 用户名均返回 401，留下 300042 字节账户键；推进时钟 115 天并触发 IP 清理后仍全部存在。不是负载压测，也未实际使服务 OOM，但已证明新增的无界保留路径。

应限制输入并控制不存在账户/全字典容量，保留合法账户跨 IP 的防护。进程内限流本身是已接受限制，与此新增内存保留问题分开。

### F07 — HIGH 相关既有安全债务：完整 OCR 日志链并未脱敏

位置：`backend/app/services/ai_service.py:130,184-198`；`ai_gateway.py:92,154-159`。

使用合成秘密标记模拟 HTTP 503 provider error，fallback warning 输出标记，交给 gateway writer 的 error 也含标记；只有 Capture adapter 自己的 warning 已脱敏。探针没有连接数据库，持久化结论仅到“传给 writer 的对象含敏感内容”，未声称实际落库。

此行为在 HEAD 已存在，不归为 PR-14 新引入；但“无敏感细节日志”应限定为两个 Capture adapter。完整日志链的风险仍需安全处理，不能因新 adapter 测试通过而关闭。

### F08 — MEDIUM：未接线的 backfill 被计为 PASS

位置：`week4/evidence/gate/week4-gate-matrix.md:22`；`backend/tests/test_ai_governance.py:244-263`；任务 `week4/tasks/pr-19.md:94-102,120,155`。

helper 测试直接调用 backfill，不等于用户确认 endpoint→实体创建→AiRun 回填。治理文档和总结如实写 NOT_YET_WIRED/延期，但矩阵写 `PASS (prospective)`，证据不足。放弃创建允许 NULL，不等于确认后不回填也通过。

当前 Capture 调用时 target linkage 已验证；creation-backfill 应单列 PARTIAL，补真实接线/集成验收，或取得明确延期裁决。没有把这一已披露债务误报成新运行时故障。

## 实际功能复验

原始证据目录：[`evidence/reassessment-2026-09-26/`](evidence/reassessment-2026-09-26/)。

| 验证 | 本次结果 | 证据及边界 |
|---|---|---|
| 前端全套 | PASS：70 文件 / 522 tests | frontend-tests.log |
| 主源码 tsc + test:typecheck | PASS：均 exit 0 | tsc.log、typecheck-tests.log；沿用已披露 ui-v2 test 排除，不代表该排除树类型通过 |
| Week4 后端 7 文件 | PASS：61 tests + 41 subtests | targeted.log；OCR 供应商模拟 |
| 后端全套 fresh、无 deselect | PARTIAL：883 passed / 3 failed / 9 skipped | full-suite.log；3 个失败与历史隔离债务一致，不是 0 failed |
| 迁移 | PASS：fresh 001→033、033→032→033、单 head033 | verify-upgrade/head/downgrade/reupgrade.log |
| Cloudflare build | PASS：Node24 隔离副本 exit0 | buildcf-node24-escalated.log；保留现有开发服务 |
| PG负向/并发 | PASS：live challenge阻止降级且保留033；过期后可降级；双session单次消费 | lifecycle_probes.log |
| runtime smoke | PASS：20/20 assets，23 checks，0 failed | runtime-smoke.log |
| 当前 5 条 Playwright | PASS：5/5，workers=1 | e2e.log，真实 Chromium+workerd+scratch backend；不代表 R22b 完整，见 F04 |
| smoke 单测 / scratch guard | PASS：15 / 37 tests | smoke-unit.log、scratch-guard.log |
| PR18 删除 | PASS：4 文件+1导入，共124行，无残留导入 | 本次静态搜索、前端全套、构建和runtime；未达到500行目标，不补删活代码 |
| git diff --check | PASS | 本次执行 exit0；未暂存任何文件 |

本次全套失败项：`test_public_empty_envelope_explicit`、`DashboardPr11ServiceTest::test_all_empty_answers_are_honest`、`DashboardPr11ServiceTest::test_partial_service_failure_degrades_without_raising`。上述三项在另一个全新库单独运行全部通过（excluded-isolated.log），支持顺序/数据污染判断。9 个 skip 均保留在原日志：6 个 LSR03 隔离环境未提供，3 个旧测试只接受 astra_week2_ / opencode_week2_ 库名。未将 skip 算作 PASS。

同站验证：构建 API `http://api.ci.test:18001`，预览 `http://app.ci.test:18787`，AUTH_BYPASS=false，测试管理员 seed。临时 Playwright config 仅用 Chromium `--host-resolver-rules` 将两个域名映射 loopback，并禁用测试浏览器代理；无 hosts 修改，无远端 CI。当前 E2E 同站阻碍已消除。修改仅存在临时测试 config，不修改仓库正式测试。

隔离构建过程：首次 node_modules 指向根目录的软链接被 Turbopack 拒绝，改用独立依赖副本；沙箱内编译停滞后终止自有进程，经工具审批在同一副本重跑成功。这两次属于验证环境问题，不计为产品回归。

## PR 与 Gate 重评

| 范围 | 当前判断 |
|---|---|
| PR14 | PARTIAL：分类/DTO/UI已有成果，真实错误分类和整链日志边界未闭合；供应商成功率未验证 |
| PR15 | FAIL：迁移与既有用例通过，CLI功能回归及多ceremony干扰已复现 |
| PR19 | PARTIAL：Capture关联与helper通过，确认回填集成仍未实现 |
| PR16 | PARTIAL：正常退避/重置通过，无界账户存储需处理 |
| PR17 | FAIL：本地现有5条脚本通过，原样CI配置阻断且两条业务链缺测 |
| PR18 | PASS（安全删除范围）；500行目标未达，已有说明 |
| M4 RELEASE GATE | FAIL：存在实质缺陷/覆盖缺口，不仅是授权导致的NOT_VERIFIED |

## 剩余风险与下一轮要求

这些是本次审查建议，不代表已授权实施。

| 优先级/关联 | 下一轮要求 | 复检标准 |
|---|---|---|
| P0 / F01 | 修复CI测试库配置与守卫兼容 | 原样CI环境参数通过guard、迁移及pytest；不得削弱真实库保护 |
| P0 / F02 | 统一CLI异步资源生命周期 | 同一真实HTTP server连续options、verify、失败重试均无跨loop错误 |
| P0 / F03 | 依据本次challenge定位并消费记录 | A/B并发各可验证、重复消费拒绝、过期/跨purpose/错binding拒绝，补PG并发证据 |
| P0 / F04 | 恢复R22b两条业务E2E | 真实页面错答→草稿、再答→记录；确定性seed与后端读回 |
| P0 / F07 | 修复完整调用链错误脱敏 | 合成秘密不出现在普通日志和待持久化错误/attempt数据中 |
| P1 / F05 | 结构化OCR错误跨层传递 | 原生timeout/畸形JSON分别稳定映射，非字符串巧合匹配 |
| P1 / F06 | 限制账户限流状态增长 | 长输入拒绝、随机不存在用户名有界，合法账户跨IP退避仍有效 |
| P1 / F08 | 对齐backfill实现与验收 | 真确认路径关联新实体，放弃仍NULL；或用户明确接受延期 |
| P1 / 既有债务 | 后端测试隔离 | fresh与同库重复运行不因残留污染失败，移除3个deselect |
| 待授权验证 | 真实OCR与远端CI | 合规样本10张真实基线；远端四Job和故意失败检查；本次未执行 |
| P2 / 文档一致性 | 收敛状态来源 | TRACKING第5节仍全NOT_STARTED，README/tasks仍初始状态，与总结矛盾；当前报告不覆盖历史记录 |

未执行产品代码修复、commit/push/merge、生产迁移/部署或真实供应商调用；现有 `blog_db` / `blog_v2` 未作为连接目标。仅创建独占 `astra_week4_reassess_20260926_{verify,full,isolation,e2e}` 测试库，保留以供复查，不擅自drop。

本次18001后端和18787隔离预览均已停止，既有开发服务未停止；scratch库及临时构建副本保留。

最终报告由独立 `auth_review` 只读复核：F01–F08 无实质证据越界，支持 Gate FAIL；其指出的一处文字错误已修正。主代理完成最终证据核对。
