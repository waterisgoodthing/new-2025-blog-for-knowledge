# UI V2 Design System Foundation（F3，2026-09-13）

目标：长期学习、低视觉疲劳、清晰层级、中等信息密度、克制、一致。
Token 实现：`src/components/ui-v2/tokens.css`（`--uiv2-*`，additive；
`src/styles/theme.css` / `globals.css` 本轮零修改）。

## Typography

- 字体栈复用仓库栈（PingFang SC / system-ui / Segoe UI…），等宽场景沿用系统 mono。
- 层级：xs 12 / sm 14 / base 16 / lg 18 / xl 20；正文 base，标题 lg/xl，
  辅助 xs/sm。字重 400/500/600 三档。

## Semantic Color

- brand 沿用 `#35bfab`（与 Legacy theme 一致）+ ink `#1f7a6e`（文字级对比）。
- 功能色降饱和：note `#2f7fd0` / blog `#4c9a52` / mistake `#c4554d` /
  warning `#b97f2c`，仅用于小面积标识（badge/点/边框），大面积保持中性白。
- 文字三级：primary `#24312f` / secondary `#5d6b69` / tertiary `#8a9694`。

## Spacing / Radius / Elevation

- 间距 4/8/12/16/24/32；圆角 8/12/16；阴影仅单层 sm/md。
- 禁止：大面积渐变、过量玻璃拟态、发光、高饱和大面积色块、无意义动画、
  数据大屏风格。

## Interaction State

- hover：透明度/阴影单属性变化，250ms；active 回原位；focus 可见描边；
  disabled 降透明 + 禁指针。`prefers-reduced-motion` 下关闭位移动画。

## Responsive / Density

- 断点沿用 Tailwind 默认（sm/md/lg/xl）；内容最大宽 840px（与 blog 列表一致）。
- 中等密度：列表行高 ≥40px，卡片内边距 16–24px。

## Accessibility

- 文字对比 ≥4.5:1（正文/二级）；图标按钮一律可聚焦 + aria-label；
- 错误态同时用颜色 + 文字表达，不唯颜色。
