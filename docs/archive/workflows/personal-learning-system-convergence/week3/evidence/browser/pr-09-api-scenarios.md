# PR-09-C real-browser scenarios (agent-browser / Chromium)

agent: PR-09-verify-api · date: 2026-09-24
frontend: `npm run build:cf`（`NEXT_PUBLIC_API_URL=http://localhost.:8001`，FQDN 尾点绕过 production localhost 守卫且与 preview 同 host 以共享 cookie）+ `opennextjs-cloudflare preview` workerd :8787
backend: uvicorn 127.0.0.1:8001，`ALLOWED_ORIGINS` 含 `http://localhost.:8787`，scratch DB `astra_week3_pr09_ui` @127.0.0.1:49621（经 `scripts/week3-scratch-guard.py`）
seed: 1× active+public（`my_answer=PR09BROWSERLEAK_secret_answer_9f2e`，`question_text=PR09PUBLIC_QTEXT_7c1d`）+ 1× active+private（`my_answer=PR09BROWSERPRIVATE_hidden_1a2b`）
session: agent-browser named session `pr09-api-1290319b4876`（真实 Chromium/CDP，非 jsdom）

## C.1 公共 /mistakes 三态 + retry

| 状态 | 操作 | 结果 | 证据 |
|------|------|------|------|
| populated | 1 条 active+public 时打开 `http://localhost.:8787/mistakes` | **PASS** — 渲染 `PR09 Public Card` 卡片（题目/正确答案/解析/错因说明），无 private 行 | `screenshots/pr-09-api-populated-desktop.png`、`pr-09-api-populated-mobile-390.png`、a11y snapshot（heading "PR09 Public Card"） |
| Empty | 全部 public→private（guard SQL）后 reload | **PASS** — 显式 Empty：heading「暂无内容」+ 后端 `message`「No published mistakes yet.」 | `screenshots/pr-09-api-empty-desktop.png`、DOM read 全文 |
| error | uvicorn 停止后 reload | **PASS** — heading「加载失败」+ button「重试」 | `screenshots/pr-09-api-error-desktop.png` |
| retry | 重启 uvicorn，点击「重试」 | **PASS** — 无整页刷新回到 populated（`PR09 Public Card` 再现） | a11y snapshot 前后对比 |

## C.2 admin publish/unpublish → 公共页反映

| 步骤 | 结果 | 证据 |
|------|------|------|
| admin 登录 `/manage`（pr09-browser-admin） | **PASS** — 进入管理面板 | a11y snapshot（退出登录/进入工作区） |
| `/manage/mistakes` 列表可见两行正式错题 | **PASS** | snapshot（PR09 Private/Public Card 链接） |
| 详情页 visibility toggle「下架（设为私有）」 | **FAIL（产品缺陷 FINDING-01）** — confirm 接受后按钮仍为「下架」，visibility 未变 | `screenshots/pr-09-api-admin-visibility-toggle-fail.png`；`network requests --filter visibility`：`PATCH http://localhost.:8001/api/admin/mistakes/54453e5b-…/visibility (Fetch) 500`（OPTIONS 预检 200，PATCH 500）；DB `visibility='public', version=1` 未变 |
| 公共页反映 visibility 变更 | **PARTIAL** — 仅数据级验证：guard SQL 改 visibility 后公共页正确增/减卡片与 Empty（见 C.1）；admin UI/API 发布下架路径被 FINDING-01 阻断 | C.1 Empty/populated 截图 |

## C.3 私有内容泄漏检查（DOM 搜索）

seed 独特字符串 `PR09BROWSERLEAK_secret_answer_9f2e`（public 行的 my_answer）与 `PR09BROWSERPRIVATE_hidden_1a2b`（private 行 my_answer）：

| 页面状态 | `PR09BROWSERLEAK…` | `PR09BROWSERPRIVATE…` | `my_answer` 键名 | `PR09PRIVATE_QTEXT` |
|----------|--------------------|-----------------------|------------------|---------------------|
| 匿名 /mistakes（DOM text + body innerHTML） | 0 | 0 | 0 | 0 |
| 已登录 admin 同浏览器 /mistakes（DOM text + body innerHTML） | 0 | 0 | 0 | 0 |

期望公开内容 `PR09 Public Card` / `PR09PUBLIC_QTEXT_7c1d` 各 1 次命中（对照）。**PASS**。
注：admin 详情页（`/manage/mistakes/…`）按设计显示 `我的答案`（MistakeOut 私有字段），不在公共泄漏面。

## C.4 视口截图

- `screenshots/pr-09-api-populated-desktop.png`（1280×800）
- `screenshots/pr-09-api-populated-mobile-390.png`（390×844）
- 另存 Empty / error / admin-toggle-fail 三张（见上表）

## 负面记录

- `test_visibility_correct_version_toggles`（TestClient）与真实浏览器 PATCH 双双 500，互相印证 FINDING-01；非测试环境差异。
