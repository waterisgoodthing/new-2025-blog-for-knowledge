# UI V2 Component Inventory（F1，2026-09-13）

状态词：KEEP（复用）/ REFACTOR（候选，本轮不动）/ REPLACE / MISSING（本轮建 skeleton）。
脏文件（`manage-sidebar`、`dashboard-overview`、`notes/page`、`tag-input`、
`use-note-editor`、`feature-state`、`dashboard-content`）一律不评估为可改，
只记录复用关系。

## KEEP（稳定，直接复用）

| 组件 | 路径 | V2 用法 |
|---|---|---|
| EmptyState（variant: no-content 等） | `src/components/empty-state.tsx` | 空态统一复用 |
| AsyncStatePanel（loading/empty/error/retry） | `src/components/async-state-panel.tsx` | 异步四态复用（Week1 PR-03 已验收；未跟踪新文件，本轨只读引用） |
| AuthGate | `src/components/auth-gate.tsx` | 仅 UX 门控复用，不做安全假设 |
| DialogModal / Drawer | `dialog-modal.tsx` / `drawer.tsx` | 弹窗/抽屉复用 |
| Select / ContextMenu / DelayedTooltip | 同名文件 | 表单与菜单复用 |
| TagInput（`src/components/tag-input.tsx`） | 同名 | 以该 canonical 为准；`write/components/ui/tag-input.tsx` 差异记 REFACTOR 候选 |
| RichText / CodeBlock / MarkdownMath / MarkdownImage / MermaidBlock / MarkmapBlock / ChartBlock / DiagramViewer | 同名前缀文件 | 内容渲染复用 |
| ScrollTopButton / SortableItem / DragDropProvider / ColorPicker(+Panel) / StarRating / EditableStarRating / LikeButton / BlogToc / BlogSidebar / BlogPreview / MoveToFolderDialog / TagSuggestionDialog / SiteSettingsLoader / WIP / MobileNav / VerticalNav | 同名 | 按需复用 |

## REFACTOR（候选，本轮不改）

| 候选 | 原因 |
|---|---|
| `write/components/ui/tag-input.tsx` vs `components/tag-input.tsx` 双 tag-input | 需收敛其一，待批准 |
| `manage/components/manage-sidebar.tsx`（脏）导航分组 | IA 落定后再改，需 ownership 批准 |
| `dashboard-overview.tsx`（脏） | 数据绑定与后端 DTO 强耦合，整页重写禁止 |
| `use-note-editor.ts` 双位置（`write-note/hooks` vs `hooks/`，后者未跟踪） | 编辑器收敛候选 |
| Card（`card.tsx`，home 卡片定位 props） | 通用 Card 语义待统，V2 新建 `ui-v2/Card` 不污染旧版 |

## REPLACE

无（本轮不替换任何线上组件）。

## MISSING（本轮在 `src/components/ui-v2/` 建最小 skeleton）

Button / Card / Badge / Skeleton / Progress / SectionHeader / PageHeader /
ErrorState（EmptyState 已有则复用，ErrorState 独立建）。
每项：`types.ts` 复用 contract + 纯展示组件 + `source` 标注位，不接真实 API。
