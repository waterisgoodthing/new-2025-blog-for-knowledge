# I6 验证记录

状态：`COMPLETE / PASS / I6-VERIFIED (2026-07-24)`

本文件记录 I6-01 至 I6-08 的实际执行结果。未执行源库/生产迁移、部署、推送或真实 AI 成功调用。

## 计划证据矩阵

| 层级 | 证据 |
|---|---|
| 数据库 | 022 隔离目标 current/heads、Capture/Draft/Attachment 表与约束只读核对 |
| 后端 | 上传、权限、识别成功/失败、草稿失败零污染、人工修正、版本冲突、拒绝、确认、幂等转换 |
| 前端 | Capture/Draft 状态、失败重试、人工编辑、来源显示、拒绝/确认、移动端和键盘 |
| 工程 | Python compileall、定向 pytest、Vitest 目标套件、`npx tsc --noEmit`、`npm run build`、`git diff --check` |
| 安全 | 匿名 401、私有内容不可读、路径/provider 错误不泄露 |
| 文档 | tasks 每项即时更新、risk-register、next-requirements、主 workflow 索引同步 |

## 实际结果

| 任务 | 结果 |
|---|---|
| I6-01 | 既有 `127.0.0.1:55435/pls_v2_i4_target` 只读确认 `alembic current=heads=022`；私有 Attachment/Capture/Draft 路由管理员依赖基线通过；9 项既有边界测试通过 |
| I6-02 | 管理员上传图片→创建 Capture、非法 MIME 拒绝、临时文件清理；新增 HTTP 测试 2 项通过 |
| I6-03 | Capture/识别/草稿失败矩阵与零污染验证；17 项 Capture 相关后端定向测试通过；修复缺失核心字段误报成功问题 |
| I6-04 | fake 识别/草稿成功、人工修正和失败恢复；Capture/Draft 前端定向测试 7 项通过 |
| I6-05 | Draft 状态、拒绝、版本冲突、确认和来源链验证；15 项 draft/chain 测试通过 |
| I6-06 | 重复 Capture 转换返回既有目标，来源链保留；I6 后端组合 34 项通过 |
| I6-07 | 三尺寸浏览器 fixture、失败提示、人工修正后待确认、无横向溢出、viewport 与键盘焦点证据通过 |
| I6-08 | 最终后端组合 51 passed；前端 9 files/33 tests passed；`npx tsc --noEmit`、`npm run build`（40/40 页面）、Python compileall、`git diff --check` 通过 |

全仓库 Vitest 仍有 1 个既有、非 I6 的 AI capture 路由测试失败（`useRouter` 缺少 App Router 挂载）；I6 定向 33 项全部通过，未扩大范围处理该无关失败。

## 浏览器证据

生产构建：`npm run build` 后使用独立 `next start -p 3028`。浏览器通过受控管理员 API fixture 展示既有失败 Capture，验证 `No AI provider configured` 安全文案、人工填写题面/解析/错因后状态变为 `待确认`，未展示 provider 原始错误或本地路径。

| viewport | 结果 | 截图 |
|---|---|---|
| 390×844 | 无横向溢出；人工修正；待确认 | [capture-390x844.png](./assets/capture-390x844.png) |
| 1280×800 | 无横向溢出；人工修正；待确认 | [capture-1280x800.png](./assets/capture-1280x800.png) |
| 1440×900 | 无横向溢出；人工修正；待确认 | [capture-1440x900.png](./assets/capture-1440x900.png) |
| 键盘 390×844 | 首次 Tab 聚焦人工修正题面 textarea，具备可操作焦点 | [capture-keyboard-390x844.png](./assets/capture-keyboard-390x844.png) |

viewport meta：`width=device-width, initial-scale=1`。

## 最终决定

I6-01 至 I6-08 全部完成，状态为 `COMPLETE / PASS`。真实 022 后端目标已通过组合测试；浏览器证据的受控 fixture 限制已明确记录，不等同于真实 AI provider 成功质量验收。
