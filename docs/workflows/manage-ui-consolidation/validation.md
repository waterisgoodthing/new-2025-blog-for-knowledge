# Manage UI Consolidation Validation

日期：2026-07-13  
范围：`manage`前端与测试基础设施  
结论：通过

## 1. 静态与构建验证

| 检查 | 结果 |
| --- | --- |
| `npm test` | 通过，5 个测试文件、18/18 测试 |
| `npm run test:typecheck` | 通过 |
| `npx tsc --noEmit` | 通过 |
| `git diff --check` | 通过 |
| `npm run build` | 通过，37/37 页面生成 |
| react-dom 清单与锁文件 | 均为精确 `19.2.1` |

测试覆盖：

- AI 原始错误正文不渲染，已知错误映射到固定安全摘要。
- 采集方式惰性挂载，切换后保留未提交内容。
- 审核中心单源失败、双源失败、部分成功、空态和重试。
- AI 处理记录行可聚焦并可用 Enter 打开详情。
- 移动抽屉背景隔离、Escape 恢复、跨层背景隔离和 body Portal。

说明：2026-07-12 的两次构建尝试曾停在优化编译阶段，均被主动终止。关闭临时开发服务器与浏览器会话后，2026-07-13 独立重跑成功，编译耗时 5.7 秒，问题未复现。

## 2. 真实浏览器验收

环境：Chromium（agent-browser 0.31.1）、Next.js `127.0.0.1:2026`、FastAPI `127.0.0.1:8001`。仅本地验收进程使用 `AUTH_BYPASS=true`与`AUTH_BYPASS_ALLOW=true`，未写入配置文件。

### 导航与移动抽屉

- 390 x 844 视口打开抽屉后，焦点进入第一项。
- 连续 12 次 Tab 后焦点仍位于抽屉内。
- 抽屉通过 Portal 挂到 `document.body`，高度 `844px`，与视口一致。
- 抽屉外可聚焦元素数量为 `0`；站点级底部导航位于 `inert`分支。
- Escape 关闭后焦点回到“打开导航菜单”，`inert`数量恢复为 `0`。
- `/manage/ai/runs` 的“AI 小助手”父导航带 `aria-current="page"`。

证据：[mobile-drawer-isolation.png](./assets/mobile-drawer-isolation.png)

### 核心交互

- 采集页填写“保留中的题干 20260712”，切换到图片再切回后内容仍在。
- 采集方式使用按钮组语义：`role="group"` + `aria-pressed`，不存在残缺的 `role="tab"`。
- AI 页面真实数据中未出现 `All AI providers failed`、`AI API error`或敏感模式；只显示受控摘要。
- AI 处理记录行可聚焦，Enter 后加载并展示详情；页面无横向溢出。
- 网络拦截模拟审核数据源失败后，页面显示错误和“重试”，未误显示为空列表。

### 页面与兼容性

以下 11 个路由在 390px 视口均可打开、显示正确一级标题且无页面级横向溢出：

```text
/manage/dashboard
/manage/capture
/manage/drafts
/manage/questions
/manage/mistakes
/manage/review
/manage/subjects
/manage/attachments
/manage/ai
/manage/jobs
/manage/settings
```

- 隐藏的 Jobs 与 Settings 不进入主导航，但兼容路由仍可直接访问。
- 旧 `/manage`可直接访问，历史入口未删除。
- 公开首页未捕获 `/api/admin`或`/api/ai/runs`请求，页面也未出现管理端文案。

### 缩放与长内容

headless Chromium 不响应系统级浏览器缩放快捷键，因此没有虚报快捷键缩放结果。采用 1280px 桌面在 200% 下等效的 640 CSS 像素布局复验 Dashboard、题目册、错题本和 AI 页面；页面无横向溢出，按钮无文字裁切。AI 页面截图见 [effective-200-ai.png](./assets/effective-200-ai.png)。

该方法验证响应式布局和文字容器，不等同于人工检查浏览器缩放菜单的渲染差异。剩余风险为低：项目未禁用用户缩放，390px 更窄视口也已通过。

## 3. 修复闭环

| 编号 | 结果 |
| --- | --- |
| R-01 | AI 错误改为受控分类，不返回原始正文 |
| R-02 | 采集方式切换保留未提交状态 |
| R-03 | 抽屉焦点循环、关闭恢复和背景隔离 |
| R-04 | 审核局部失败显示错误与重试 |
| R-05 | AI 记录支持键盘打开 |
| R-06 | 文案词典与圆角范围修正 |
| R-07 | 背景隔离扩展到工作区外分支 |
| R-08 | react-dom 清单与锁文件精确版本同步 |
| R-09 | 抽屉 Portal 覆盖完整移动视口 |

## 4. 边界与剩余风险

- 未修改 `backend/`、API、数据库、migration、权限或 workflow 执行机制。
- `knowledge-point-select.tsx`与旧 `/manage`中的预存大圆角不在批准范围。
- 旧 `/manage`仍使用历史认证实现，属于既有架构债务。
- 生产环境拒绝 AUTH_BYPASS 双 true 不在本任务范围。
- Vitest、Testing Library、jsdom 和测试 TypeScript 配置属于本轮新增测试基础设施。

## 5. 临时环境清理

- 临时 Next.js `2026`进程：已停止。
- 临时 FastAPI `8001`进程：已停止。
- `manage-final`浏览器会话：已关闭。
- 未创建测试数据；采集状态保留验证未提交表单。
