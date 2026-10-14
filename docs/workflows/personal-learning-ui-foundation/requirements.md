# Requirements — UI Foundation Track 第一阶段（F0–F5）

## REQ-F0 基线与审计
- R-F0-1：冻结独立前端轨基线（status + diff），区分 PRE-EXISTING 与 THIS TRACK。
- R-F0-2：完成 Repository UI Audit：路由清单、组件清单、样式/token 现状、
  API client 分层现状，只读审计，不改业务文件。

## REQ-F1 组件盘点
- R-F1-1：输出 Component Inventory，状态仅限 KEEP / REFACTOR / REPLACE / MISSING。
- R-F1-2：已有稳定组件满足需求 → REUSE，不复制 V2；需改白名单外文件 →
  REFACTOR_CANDIDATE，本轮不改。
- R-F1-3：创建前完成盘点；Button/Card/Badge/EmptyState/ErrorState/Skeleton/
  Progress/SectionHeader/PageHeader 按需新增于 `src/components/ui-v2/`。

## REQ-F2 信息架构
- R-F2-1：按真实仓库输出 Current Route → Proposed Route → Status
  （KEEP / REFACTOR / MIGRATE_LATER / LEGACY / UNKNOWN）。
- R-F2-2：目标方向：首页；学习（今日任务/题库/错题/复习）；知识
  （科目/知识点/笔记）；分析（掌握度/薄弱点/学习趋势）；资料；设置。
- R-F2-3：本轮不做大规模路由迁移。

## REQ-F3 设计系统
- R-F3-1：建立 Typography / Semantic Color / Spacing / Radius / Elevation /
  Interaction State / Responsive / Accessibility 基础（additive token）。
- R-F3-2：目标：长期学习、低视觉疲劳、清晰层级、中等密度、克制、一致。
- R-F3-3：禁止：大面积渐变、过量玻璃拟态、发光、高饱和大面积色块、无意义动画、
  数据大屏风格。

## REQ-F4 契约 / Mock / Adapter 骨架
- R-F4-1：UI Contract（如 ReviewTask / MasteryScore）仅为 UI-facing，
  架构保持 Backend DTO → Adapter → UI Contract → UI Component。
- R-F4-2：Backend DTO 不满足 → 记 Gap，不改后端 DTO（ ever ）。
- R-F4-3：Mock（Dashboard/Review/Mistakes）标记 `mock` 来源，不进真实业务路径；
  覆盖 normal / empty / loading / error / partial / overdue。
- R-F4-4：Mastery 无算法；数据不足时 UI 表述“暂无足够数据 / 数据积累中”，
  禁止虚假精确度；`source: backend | mock | estimated` 必填。

## REQ-F5 验证与文档
- R-F5-1：执行 typecheck / frontend tests / lint / build /
  `git diff --check`（按仓库实际 scripts），结果记 PASS / PARTIAL / FAIL /
  NOT_APPLICABLE，不把未运行写成 PASS。
- R-F5-2：Backend pytest 仅在影响共享契约或治理要求时运行，且用隔离库，
  不污染 Week2 环境。本轨默认不需要新 DB 实例，禁止用 Week2 main scratch /
  真实 blog_db / 生产库做产品写入。
- R-F5-3：交付 workflow 五件套 + `docs/ui-v2/` 文档 + 合规核对
  （Week2/Backend/Migration/Auth/脏文件零修改）。

## 非目标（本轮禁止）
Review 六档评分、Today 完整页、Capture、Auth/登录/权限、public/private ownership、
Question practice、Mastery/Review 调度算法、Dashboard/Notes/Mistakes/Review 整页重写、
UI-03~UI-12。
