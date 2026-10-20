# Week 1 证据索引

本目录保存真实浏览器截图。运行于 2026-09-09 的原始文本日志保留在 `/tmp/astra-week1-20260908/`；下表记录验收摘要与 SHA-256，便于核对原始文件是否发生变化。日志不含数据库口令或会话 cookie。

| 原始文件 | SHA-256 | 验收摘要 |
| --- | --- | --- |
| `frontend-full-test.log` | `73fb4c25814839d210388a16701312fb7bdd38bc39554dfdc18ec01cb99d00f5` | 43 files / 395 tests PASS |
| `backend-full-scratch.log` | `fc4f92a00e95f1b16ab94ee84df6b572048549992eb9d96287fefd9f0989d016` | scratch@027，416 passed / 7 skipped |
| `build-cf.log` | `dddbf188e211fe22ec64145f8578c6f2d149a7a5c92e8e9480d4bd7f8e89d410` | fresh Next.js + OpenNext build PASS |
| `runtime-smoke-gate.log` | `955650bb5341ca30b76131a5b2620fc76bafc8815d9f6e4a23988ad8ce27ecbd` | exit 0，assets 20/20，checks 23/23 |
| `runtime-smoke-negative.log` | `6f18e61752e001ac2920719db51e106e26a347a4c9c050d915fc58d174e57418` | 失效 API health，exit 1 |
| `pr02-browser-production.log` | `b745bc21fd3d5c359b9f249a9669072e2792f95777dc58c00a193f29a7d891c6` | workerd Chromium 19/19 PASS |
| `pr03-browser-production.log` | `355dadbb4f96b0ab02db002456da71fa4dc9ab1d31fdd2dd626b46bef5baa229` | workerd Chromium 9/9 PASS |
| `gate-authoring-db.log` | `1d011adb2ec397666379764dad076e4f8a93c5a6e142244b2afd13511cfc3cc4` | Note revision 2；Blog published revision 4 |
| `pr04-replay.log` | `bce7d69cd09c1101b7a46cffc1e8a76ecdcad9f6bf40035499a01cee878bb6bd` | fresh/existing upgrade + downgrade PASS |
| `pr04-partial-upgrade.log` | `4a60824d6ef477b5679a585adf8dc31e4aab773113bab9d41b91c0f5d6edf871` | partial schema fail-closed PASS |
| `pr04-runtime-evidence.json` | `303015e3fcd5faffac5318eadc7972eb81726b833523e219799e303d43b6ec71` | health 200、POST 201、持久化读取 PASS |
| `pr04-gemini-review.log` | `c334d2bf3ad7c9d4a0e99eb6569b596e780ceb312b032e7905e8bea0426eb5e4` | G2 独立评审 PASS |
| `week1-gate-gemini-review.log` | `7c908afbd52a21d547da4832b24a694c04e5418886d9bdd821bd1191b5880f85` | Week 1 Gate 独立评审 PASS，0 blocker |

## 截图

- `pr02-desktop-editor.png`：桌面端 ContentEditor。
- `pr02-mobile-drawer.png`：移动端属性抽屉。
- `pr03-notes-retry-success.png`：`/notes` 错误恢复。
- `pr03-dashboard-retry-success.png`：Dashboard 错误恢复。

本任务创建的 8787、8001、55439 运行进程和 scratch PostgreSQL 数据库已在验收后清理。历史 8000 与 2025 服务未触碰。
