# 路线图 2026-09（唯一活文档）

> 本文档取代 `refactor-plan-2026-08-02.md`、`refactor-plan/`、`refactor-executive-summary.md`、`refactor-github-opensource-report.md` 四份重叠报告，作为唯一滚动路线源。历史过程证据保留在 `docs/workflows/`（后续归档到 `docs/archive/`），不再新增同级别过程文档；小任务不建 workflow 文件夹（比例性原则见 AGENTS.md §2）。

## 路线规则

1. **薄片垂直交付**：每个切片 ≤5 个工作日、可独立部署、CI 绿灯为完成门禁。
2. **完成的定义包含拆除**：任何替换/切换类工作项，验收必须包含旧路径删除或归档，否则不计完成。
3. **引用现行契约**：所有计划引用 AGENTS.md §4（`admin_session` cookie + `get_current_admin`）；与契约冲突的旧计划条款一律作废（含 8/02 计划的 jose/JWT 中间件条款）。
4. **先删除后新建**：视觉/组件工作前先完成对应拆除项。

## 当前基线（2026-08-29 实测）

| 项 | 状态 | 证据 |
|---|---|---|
| 安全加固 S1–S6（门禁/脱敏/端点/常数时间比较） | ✅ 已完成并审查 | `docs/workflows/security-findings-remediation/` |
| 迁移 026 本地落库 + 模型对齐（mistake_id） | ✅ | 同上 Addendum 1/2 |
| CI（真实 Postgres + 全链迁移 + backend/.venv + vitest 补齐待做） | ✅ 绿 | run 33248560018 |
| 后端测试 | 412 通过 / 6 跳过 | 本地实测 |
| 前端测试 | 374 通过（CI 尚未运行，W1 补） | 本地实测 |
| 死路由树 `/write*` `/write-note*` `/write-mistake*` `/mistakes/review` | ❌ 5,782 行仍编译 | next.config.ts redirects vs src/app/* |
| 双 manage UI（760 行 page.tsx vs (workspace)/ 模式） | ❌ 并存 | src/app/manage/page.tsx |
| 5 个列表页重复 CRUD 脚手架 | ❌ ~1,000 行重复 | projects/share/pictures/bloggers/snippets |
| 页面 metadata/OG | ❌ 0/49 页 | 仅 layout.tsx 有 |
| 视觉整合 VSC | ❌ 仅 VSC-01 基线，token 零落地 | visual-system-consolidation/ |
| 编辑器收敛 | ❌ 仅方案 A 设计，未批准实施 | editor-convergence/ |
| Markdown 加固渲染器 | ❌ PoC 隔离，生产仍旧渲染器 | src/lib/markdown-poc/ |
| LCP 实测 | ❌ RISK-PRA-001 未处理 | page-render-timing-validation/ |
| lint / dependabot / pre-commit | ❌ 全无 | — |
| 重负载库加载 | ✅ 全动态导入（15 处） | grep 实测 |
| public/ 体积 | ⚠️ 40MB（24MB 版权音乐） | — |

## 切片路线（每周一片，可部署）

### W1 — 收割周（拆除 + 护栏）🔴 最高优先
- 删除 4 棵死路由树（5,782 行）及仅其引用的模块；保留 next.config 重定向一周期后移除。
- `manage/page.tsx` 收敛进 `manage/(workspace)/` 模式（5 个内联 tab 拆出）。
- 5 个列表页抽 `useContentCollection` hook + 共用管理弹窗。
- 护栏：CI 前端 job 补 `npm test` + `test:typecheck`；加 ruff + eslint + dependabot（各 ~半日）。
- **验收**：src 净减 ≥6,000 行；全部测试绿；UI 无可见变化；CI 含前端测试。

### W2 — 视觉系统落地 🟡
- 批准 VSC-02/03（其余 VSC 项延后）：editorial token 落进 `theme.css`（Tailwind 4 变量扩展）；浮动 sticky 顶栏统一桌面/移动导航（替代 VerticalNav + 底部 MobileNav）；Modal/Drawer/Popover 可访问性分层合同。
- **验收**：全站单一导航形态；浮层键盘可操作、焦点受管理；视觉基线截图对比无回归。

### W3 — 编辑器收敛（方案 A，缩范围）🟡
- 仅对 capture / notes / mistakes 三个编辑器落地共享原语；不建 UnifiedEditor。
- **验收**：一个共享原语库，三编辑器接入；AuthGate 覆盖核对表通过。

### W4 — 渲染管线统一 🔴 唯一安全相关项
- 补 `rehype-sanitize` 白名单（D-05 缺口）→ 将加固渲染器 M7 提升为生产路径（`use-markdown-render` 切换实现）→ 删除/归档 `src/lib/markdown-poc/`。
- **验收**：安全测试在生产路径通过；mermaid/markmap/math/chart 截图对比无回归；PoC 树出库。

### W5 — 可见性周（SEO + 性能 + a11y）🟢
- 详情页瘦服务端包装 + `generateMetadata`（blog/notes 优先）；GA ID 移入环境变量。
- Lighthouse CI 门禁（LCP < 2.5s，闭环 RISK-PRA-001/002）；like-button 定时器清理；图标按钮 aria-label 专项。
- **验收**：分享链接带真实标题/OG；Lighthouse 门禁进 CI；a11y 抽查清单通过。

## 并行 / 决策点（需要你拍板）

| 决策 | 建议 | 影响 |
|---|---|---|
| D1 生产迁移 026 窗口 | 排期执行（需 CREATEROLE 超级用户 + 共享实例角色/REVOKE 评估；演练基建已备） | LSR-03 从 FAIL 转入收尾或正式归档 |
| D2 统一创作面板（cmdk + Radix） | 缓议：属新功能非技术债，W1–W5 完成后再评估；jose 条款已作废 | 执行摘要 Phase 1 三件事仅剩面板 |
| D3 public/ 音乐外迁 | 迁 CDN/R2（开源报告已推荐 boto3/R2），顺带解决版权暴露 | 仓库 -24MB |
| D4 reactStrictMode: false | W2 结束后试点开启一轮，验证无隐藏副作用后常开 | 暴露 effect 类 bug |

## 明确不做（冻结清单）

- ❌ jose/JWT 中间件、任何第二套认证（契约冲突）。
- ❌ UnifiedEditor 大一统、style-dictionary、新状态管理库。
- ❌ 遗留 note 型错题域的新功能扩展（只维护，随 D1 收尾）。
- ❌ 在 W1–W5 期间新增顶层路由或重写后端边界。

## 完成后（W6+ 候选池）

监控/告警、覆盖率工具、SBOM/NOTICE、对象存储迁移、cmdk 创作面板、`refactor-plan*` 四份报告归档删除（本文档接管后）。
