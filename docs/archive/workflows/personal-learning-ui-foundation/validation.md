# Validation — UI Foundation Track（F5 填写，状态词仅限 PASS / PARTIAL / FAIL / NOT_APPLICABLE）

> 不把未运行写成 PASS。Backend pytest 仅在影响共享契约时运行（本轨默认不跑）。

| 项 | 命令 | 结果 | 证据 |
|---|---|---|---|
| typecheck | `npx tsc --noEmit` | PASS | 2026-09-13 实测 exit 0，全仓库（含新增 ui-v2 文件）零错误 |
| frontend tests | `npx vitest run src/{contracts,mocks,adapters,components,features}/ui-v2` | NOT_APPLICABLE | 无 test 文件（"No test files found"）；本轨未改任何既有文件，无回归面 |
| lint | 仓库无 lint script | NOT_APPLICABLE | `package.json` scripts 经查无 lint 项 |
| build | `npm run build` | PASS | 2026-09-13 实测 exit 0，全路由 prerender/SSR 正常 |
| git diff check | `git diff --check` | PASS | exit 0，无空白错误 |
| backend pytest | 未运行 | NOT_APPLICABLE | 本轨未触共享契约；Week2 隔离环境未动 |

## 合规核对（F5 对比基线填写）

| 项 | 预期 | 实际 |
|---|---|---|
| Week2 files modified（本轨新增） | NO | NO（`git status` 对比基线：modified 29 项与基线完全一致） |
| Backend modified | NO | NO |
| Migration modified | NO | NO |
| Auth modified | NO | NO |
| Pre-existing dirty files modified | NO | NO（新增 untracked 仅白名单：`docs/ui-v2/`、本 workflow、`src/{contracts,mocks,adapters,components,features}/ui-v2`） |

基线：`evidence/baseline-status-frontend.txt`、`evidence/baseline-frontend.diff`。
判定方法：`git status --short` 与基线 diff 对比，本轨新增文件仅限白名单路径。
