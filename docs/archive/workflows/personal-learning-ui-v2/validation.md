# Validation — UI V2 Full Implementation（状态词仅限 PASS / PARTIAL / FAIL / NOT_APPLICABLE）

> 不把未运行写成 PASS。Backend pytest 仅在影响共享契约时运行（本轨不碰后端，
> 默认 NOT_APPLICABLE）。jsdom 测试不作为真实浏览器行为证据（见浏览器项）。

| 项 | 命令 | 结果 | 证据 |
|---|---|---|---|
| typecheck | `npx tsc --noEmit` | PASS | 2026-09-15 exit 0（修复 PageStateView 路径后全仓库零错误；复检后重跑仍 exit 0） |
| frontend tests | `npx vitest run`（全仓库） | PASS | 2026-09-15：54 文件 / 450 测试全过（含 ui-v2 11 文件 / 55 测试） |
| lint | 仓库无 lint script | NOT_APPLICABLE | `package.json` scripts 经查无 lint 项 |
| build | `npm run build` | PASS | 2026-09-15 exit 0，全路由 prerender/SSR 正常（`/tmp/uiv2-final-build.log`） |
| git diff check | `git diff --check` | PASS | 2026-09-15 exit 0 |
| backend pytest | 未运行 | NOT_APPLICABLE | 本轨未触共享契约 |
| browser validation | 真机抽查 PASS（路由面）/ V2 挂载待预览路由 | 2026-09-20 agent-browser：home 375/768/1024/1440 + /notes + /mistakes 截图 PASS；Tab 可达；零 page errors；:2025 旧实例 HMR 假象已排除 |

## 合规核对（本轨基线 `baseline-status-uiv2.txt`，终验 2026-09-15）

| 项 | 预期 | 实际 |
|---|---|---|
| Week2 files modified（本轨新增） | NO | NO（独立评审复核：31 tracked-modified 与基线完全一致，零差异） |
| Backend modified | NO | NO |
| Migration modified | NO | NO |
| Auth modified | NO | NO |
| Pre-existing dirty files modified | NO | NO |
| 本轨新增文件仅限白名单路径 | YES | YES（85 新文件全在 ui-v2 命名空间 + 本 workflow；唯一 status delta 即本 workflow 目录） |

判定方法：`git status --short` 与基线逐行 diff（`/tmp/uiv2-final-status.txt`），
tracked 零差异；独立评审（REV-UIV2-01）逐文件确认。

## 分阶段验证记录

| 阶段 | typecheck | tests | 备注 |
|---|---|---|---|
| U1 App Shell | PASS（终验） | 12/12 PASS | 导航配置 + shell 组件 |
| U2 Dashboard | PASS（终验） | 7/7 PASS | adapter 降级 + hook retry |
| U3 Today | PASS（终验） | 5/5 PASS | GAP-001 诚实标注；T-U3-3 BLOCKED |
| U4 Mistakes | PASS（终验） | 6/6 PASS | canonical 适配 + filter 矩阵 |
| U5 Review | PASS（终验） | 3/3 PASS | 无自创评分；T-U5-3 BLOCKED_BY_WEEK2 |
| U6 Questions | PASS（终验） | 4/4 PASS | 无正确性判定；GAP-006 确认 |
| U7 Knowledge | PASS（终验） | 3/3 PASS | 学习信号 unknown/null |
| U8 Notes | PASS（终验） | 3/3 PASS | editor 未动；slug 编码 + null-tags |
| U9 Analytics | PASS（终验） | 5/5 PASS | 无自创算法；全 null 空态 |
| U10 Resources | PASS（终验） | 4/4 PASS | attachments 映射；GAP-007 确认 |
| U11 Settings | PASS（终验） | 2/2 PASS | Auth 未碰；视图本地偏好 |
| U12 Responsive | 静态 PASS | — | 375/768/1024/1440 代码审计；真机 NOT_VERIFIED |
| U13 Accessibility | 静态 PASS | 断言覆盖 | tertiary→secondary；focus/touch 补齐；progressbar 命名 |
| U14 Integration | PASS | 链路 grep | 组件零 lib/api；adapter 纯 type-only；mock 全 source 标注 |
| U15 Final QA | PASS | 全量 450/450 | 路由冒烟 19/19；回归全过 |
| Review fixes | PASS（终验） | 55/55 | M1/M2/L2/L3 复检 FIXED；H1→B-003 |

## U12 Responsive 结果矩阵（静态审计，2026-09-15）

| 断点 | navigation | sidebar | tables | cards | forms | dialogs | overflow | touch target | density |
|---|---|---|---|---|---|---|---|---|---|
| 375 | PASS（横滑 pills） | N/A（隐藏） | N/A（无表格） | PASS（单列+break-words） | PASS（wrap+40px） | N/A（未建） | PASS（min-w-0） | PASS（≥40px） | PASS（中等） |
| 768 | PASS | PASS（显示） | N/A | PASS（2 列） | PASS | N/A | PASS | PASS | PASS |
| 1024 | PASS | PASS | N/A | PASS | PASS | N/A | PASS | PASS | PASS |
| 1440 | PASS | PASS | N/A | PASS（max-w 约束） | PASS | N/A | PASS | PASS | PASS |

注：sidebar 在 <md 隐藏、≥md 显示；“表格/弹窗 N/A”指 V2 未新建表格与对话框
（复用现有 DialogModal/Drawer，经 Component Inventory KEEP 引用）。
真机截图验证：NOT_VERIFIED（环境限制），记为剩余风险。

## U13 Accessibility 结果矩阵（2026-09-15）

| 项 | 结果 | 证据 |
|---|---|---|
| keyboard navigation | PASS | 全部交互为原生 button/input/select/a；测试全经 getByRole 定位 |
| focus-visible | PASS | 链接/按钮/表单控件全覆盖；Uiv2Button 补齐（review fix） |
| semantic HTML | PASS | nav/header/main/section/fieldset/legend/ul/li |
| label | PASS | filter/search/settings/radio 全 labelled |
| aria-label/describedby | PASS | nav/breadcrumb/loading status/progressbar 命名 |
| dialog focus | NOT_APPLICABLE | V2 未新建对话框 |
| contrast | PASS（静态） | tertiary→secondary；白字底由 brand→brand-ink |
| disabled | PASS | 查看解析 disabled+opacity+文字说明 |
| loading/error | PASS | role=status/alert+文字 |
| 非颜色状态表达 | PASS | badge 全带文字；Due/逾期等文本断言覆盖 |

## 独立评审

- REV-UIV2-01：ACCEPT_WITH_CONCERNS（H1/M1/M2/L1–L4，无 BLOCKER；no-touch CONFIRMED）。
- REV-UIV2-02（复检）：M1/M2/L2/L3 FIXED；B-003 实施后关闭；ACCEPT_WITH_CONCERNS；
  无新增 BLOCKER/HIGH。

## 2026-09-20 “全部授权”执行轮验证（终验二）

| 项 | 命令 | 结果 | 证据 |
|---|---|---|---|
| typecheck | `npx tsc --noEmit` | PASS | exit 0（含 PR-08 target_id 修正） |
| frontend tests | `npx vitest run` | PASS | 58 文件 / 471 测试（含 review-queue 4 + 外部 14 observed） |
| backend tests | pytest `tests/`（隔离 scratch， vacancy blog_db） | PASS | 486 passed / 6 skipped（含 reanswer 26 + scheduling 9 + replay） |
| migration | 空库 upgrade head + 030 downgrade/re-upgrade | PASS | head 单 030；循环干净 |
| build | `npm run build` | PASS | exit 0 |
| git diff check | `git diff --check` | PASS | exit 0 |
| 合规 | tracked-M 对照基线 | PASS | 新增 7 tracked 文件全在授权集（PR-07×5 + PR-08×1 + B-003×1）；其余 30 项与基线一致 |
| browser（路由面） | agent-browser 自建 :2026 | PASS | home 四断点 + /notes + /mistakes；零 page errors；:2025 旧实例 HMR 假象排除 |
| browser（管理链） | — | NOT_DONE | admin 凭证边界；自动化链 + 组件测试替代 |

## 独立评审（执行轮）

- PR-06：ACCEPT_WITH_CONCERNS（3 LOW 已落实）；G0/G2 PASS。
- PR-07：ACCEPT_WITH_CONCERNS（M1/L1/L2 已落实；M3 为 D7 条件；余备注/递延）；G0/G2 PASS。
- PR-08：ACCEPT_WITH_CONCERNS（44px/推荐视觉/adapter 诚实化已落实；动效与人工链为记录递延）；G0/G3 PASS。
- Week2 Gate：NOT_VERIFIED（仅余人工浏览器全链，凭证边界）。
