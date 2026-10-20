# 遗留 Overlay 消费者迁移启动 Prompt — 给 DeepSeek

你是本仓库的前端实施智能体，任务是 **将 17 个旧 overlay 组件的消费者迁移到 UI V2 组件**。只做迁移，做完停下汇报。

## 0. 开工前必读

1. 先读 `AGENTS.md`（仓库强制规则）。
2. 本项目的 Next.js 版本有破坏性变更，写代码前查 `node_modules/next/dist/docs/` 中相关指南。
3. 运行 `git status --short`。Phase 1–6 均已提交并推送（最新 `9f0c268`）。若开工时有未提交改动，视为用户改动，**不要回滚、重排、格式化或覆盖**。

## 1. 现场事实（已核实，优先于文档中的描述）

- 仓库：`/Users/limengyang/2025-blog-public`，分支 `refactor/baseline`
- 基线：`npx tsc --noEmit` 0 errors；`npx vitest run` 79 files / 669 passed；`npm run build` 成功
- 前端：Next.js 16 + React 19 + Tailwind 4 + `motion` + `lucide-react`；测试 Vitest + `@testing-library/react`
- **UI V2 组件**（`src/components/ui-v2/`）：
  - `Modal.tsx` — 替换旧的 `DialogModal`
  - `ContextMenu.tsx` — 替换旧的 `ContextMenu`
  - `Tooltip.tsx` — 替换旧的 `DelayedTooltip`
  - `Drawer.tsx` — 未在待迁移列表中使用
- **旧组件**（`src/components/`）：
  - `dialog-modal.tsx` — 13 个消费者
  - `context-menu.tsx` — 2 个消费者
  - `delayed-tooltip.tsx` — 2 个消费者
  - `drawer.tsx` — 0 个消费者（已在 Phase 2/3/4 迁移完）

## 2. 任务：17 个消费者逐个迁移

### 2.1 迁移清单

**DialogModal → Modal（13 个文件）**：
1. `src/app/(home)/config-dialog/index.tsx`
2. `src/app/bloggers/components/avatar-upload-dialog.tsx`
3. `src/app/bloggers/components/create-dialog.tsx`
4. `src/app/image-toolbox/page.tsx`
5. `src/app/pictures/components/upload-dialog.tsx`
6. `src/app/projects/components/image-upload-dialog.tsx`
7. `src/app/share/components/logo-upload-dialog.tsx`
8. `src/app/projects/components/create-dialog.tsx`
9. `src/app/snippets/page.tsx`
10. `src/app/share/components/create-dialog.tsx`
11. `src/components/chart-block.tsx`
12. `src/components/diagram-viewer.tsx`
13. `src/components/markmap-block.tsx`

**ContextMenu → ContextMenu（2 个文件）**：
14. `src/app/notes/components/knowledge-sidebar.tsx`
15. `src/app/notes/page.tsx`

**DelayedTooltip → Tooltip（2 个文件）**：
16. `src/app/write-note/components/note-templates.tsx`
17. `src/app/write-note/components/note-toolbar.tsx`

### 2.2 迁移规则

#### DialogModal → Modal

旧 API（`src/components/dialog-modal.tsx`）：
```tsx
<DialogModal
  isOpen={open}
  close={() => setOpen(false)}
  title="标题"
  description="描述"
  actions={<Button>确认</Button>}
>
  {children}
</DialogModal>
```

新 API（`src/components/ui-v2/Modal.tsx`）：
```tsx
<Modal
  open={open}
  onOpenChange={setOpen}
  title="标题"
  description="描述"
  footer={<Button>确认</Button>}
>
  {children}
</Modal>
```

**迁移步骤**：
1. 替换 import：`from '@/components/dialog-modal'` → `from '@/components/ui-v2/Modal'`
2. 替换组件名：`<DialogModal>` → `<Modal>`
3. prop 映射：
   - `isOpen` → `open`
   - `close` → `onOpenChange`（注意：新 API 传入 setter，不是 `() => setter(false)`）
   - `actions` → `footer`
   - `title`/`description`/`children` 保持不变
4. 如果旧代码传的是 `close={() => setOpen(false)}`，新代码改成 `onOpenChange={setOpen}`

#### ContextMenu → ContextMenu

旧 API（`src/components/context-menu.tsx`）：
```tsx
<ContextMenu
  trigger={<Button>右键</Button>}
  items={items}
/>
```

新 API（`src/components/ui-v2/ContextMenu.tsx`）：
```tsx
<ContextMenu
  trigger={<Button>右键</Button>}
  items={items}
/>
```

**迁移步骤**：
1. 替换 import：`from '@/components/context-menu'` → `from '@/components/ui-v2/ContextMenu'`
2. 组件名和 props 完全一致，API 兼容
3. 如果有 `type ContextMenuItem` 的导入，同样从新路径导入

#### DelayedTooltip → Tooltip

旧 API（`src/components/delayed-tooltip.tsx`）：
```tsx
<DelayedTooltip content="提示文本">
  <Button>按钮</Button>
</DelayedTooltip>
```

新 API（`src/components/ui-v2/Tooltip.tsx`）：
```tsx
<Tooltip content="提示文本">
  <Button>按钮</Button>
</Tooltip>
```

**迁移步骤**：
1. 替换 import：`from '@/components/delayed-tooltip'` → `from '@/components/ui-v2/Tooltip'`
2. 替换组件名：`<DelayedTooltip>` → `<Tooltip>`
3. props 保持不变（`content`/`children` 一致）

### 2.3 注意事项

- **零视觉改动**：不要调整布局、间距、颜色、尺寸，只替换底层组件
- **零功能变更**：不要改业务逻辑、表单校验、API 调用
- **保留现有测试**：不删除任何 `*.test.tsx`，迁移后确保测试仍然通过
- **不碰 manage 页面**：`src/app/manage/` 下的页面不在此次范围，留给下一个任务
- **不删旧组件**：`dialog-modal.tsx`/`context-menu.tsx`/`delayed-tooltip.tsx` 迁移完后保留（等全部消费者迁完再统一删）

## 3. 验收

| 检查 | 要求 |
|---|---|
| `npx tsc --noEmit` | 0 errors |
| `npx vitest run` | 全部通过，数量 ≥ 669 |
| `npm run build` | 成功，路由表与基线一致 |
| `git diff --check` | clean |
| `grep -r "from '@/components/dialog-modal'\|from '@/components/context-menu'\|from '@/components/delayed-tooltip'" src --include="*.tsx" \| grep -v manage` | 0 results（manage 之外的旧组件消费者全部迁完） |

## 4. 汇报格式

先给结论（PASS / PARTIAL / FAIL / BLOCKED / NOT_VERIFIED），然后：

- **Changes**：17 个文件的迁移清单，每个文件写明 `DialogModal→Modal` 或 `ContextMenu→ContextMenu` 或 `DelayedTooltip→Tooltip`
- **Verification**：每条命令和结果
- **Remaining**：如果有文件因为某种原因无法迁移（例如 API 不兼容、业务逻辑冲突），列出来并说明原因

如果用了独立子代理审查，写明审查者 ID 和它报的问题；没有就写"未做独立审查"。
