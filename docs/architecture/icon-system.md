# 图标系统规范

相关文档：[技术栈](./tech-stack.md)、[前端结构](./frontend-structure.md)、[渲染系统](./rendering-system.md)。

## 1. 图标系统目标

建立稳定的语义名称、统一视觉参数与可访问性规则，避免页面直接依赖具体图标实现、多个图标库和内联 SVG 混用。

## 2. 目标技术栈

全站统一使用 `lucide-react`，通过 `AppIcon` 做语义封装，不混用多个图标库。

```text
src/components/icons/
├── AppIcon.tsx
├── icon-map.ts
└── types.ts
```

## 3. AppIcon 语义封装

业务代码优先使用 `<AppIcon name="note" />`，由 `icon-map` 决定具体 Lucide 图标。`name` 使用受控联合类型；尺寸、线宽、颜色和 `aria-hidden` 默认值集中处理。替换具体图标不应要求修改所有页面。

## 4. 图标语义映射

| 语义名 | Lucide 图标 |
|---|---|
| `blog` | `FileText` |
| `note` | `BookOpen` |
| `mistake` | `AlertTriangle` |
| `ai` | `Sparkles` 或统一选定的 `Brain` |
| `review` | `CalendarCheck` |
| `search` | `Search` |
| `tag` | `Tags` |
| `edit` | `Pencil` |
| `private` | `Lock` |
| `settings` | `Settings` |
| `upload` | `Upload` |
| `image` | `Image` |
| `code` | `Code` |
| `diagram` | `Workflow` |
| `mindmap` | `Network` |

同一语义只能保留一个默认映射；如 `ai` 在实施阶段选定 `Sparkles` 或 `Brain` 后应全站一致。

## 5. 尺寸、线宽与颜色规范

- 默认 `size` 为 16 或 18，由组件场景 token 决定。
- 默认 `strokeWidth` 为 1.75 或 2，全站选定后保持一致。
- 默认继承文本颜色，不使用彩色图标表达普通导航或操作。
- 小图标不得单独承担复杂状态；危险、成功等状态同时提供文字或其他非颜色线索。

## 6. 使用规则

- 优先通过 `AppIcon name` 使用语义图标。
- 图标旁已有可见文字时通常设为装饰性 `aria-hidden`。
- icon-only button 必须由按钮提供 `aria-label` 或等价可访问名称。
- 仅底层 icon system 文件直接 import `lucide-react`；特殊品牌标志或确无语义映射的例外需记录理由。

## 7. 迁移策略

先只读列出现有图标来源与语义，再冻结 icon map；随后按共享导航、管理操作、业务页面分批替换。每批验证视觉、按钮名称、bundle 和无图标回退。本轮不执行盘点、不安装依赖、不修改组件。

## 8. 禁止事项

- 不混用 `react-icons`、Heroicons、Font Awesome 和自定义 SVG。
- 不在普通 UI 中用 emoji 替代主图标。
- 不在每个页面随意直接引入图标库。
- 不用颜色作为唯一状态表达。
- 不为轻微视觉偏好绕过 `AppIcon` 创建重复图标。
