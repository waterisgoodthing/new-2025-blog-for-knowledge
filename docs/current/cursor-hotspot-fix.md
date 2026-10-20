# 自定义鼠标指针修复记录

**日期**: 2026-10-17  
**状态**: ✅ 已修复（临时方案）  
**优先级**: P2 — 体验优化

---

## 问题描述

自定义鼠标指针（`/images/cursor.svg`）存在两个问题：

1. **Hotspot 偏移**：点击位置与视觉箭头尖端不对齐，向下偏移约一行高度
2. **样式切换**：在某些交互元素（button/a）上鼠标在自定义样式和系统 pointer 之间来回切换

根本原因：
- 原 SVG 的箭头起点不在 `(0, 0)`，而是在 `(3.98, 0.637)`，且 filter 阴影进一步偏移
- `tokens.css` 和 `article.css` 中的 `cursor: pointer` 覆盖了全局设置

---

## 解决方案

### 1. 重新绘制精准 SVG

创建 `/public/images/cursor-precise.svg`：

- 箭头尖端严格在 `(0.5, 0.5)` 原点
- 16×24 标准比例
- 移除阴影偏移（改用 `feDropShadow` 避免影响 hotspot）

### 2. 全局 Cursor 继承策略

在 `globals.css` 中：

```css
html {
  cursor: url(/images/cursor-precise.svg) 0 0, auto;
}

* {
  cursor: inherit !important;
}

/* 保留交互状态的视觉反馈 */
button:not(:disabled),
a,
[role="button"],
[onclick],
input[type="checkbox"],
input[type="radio"],
select {
  cursor: pointer !important;
}

:disabled,
[aria-disabled="true"] {
  cursor: not-allowed !important;
}
```

**策略**：
- 全局统一自定义样式
- 交互元素（button/a/checkbox）用系统 `pointer`（保留用户习惯）
- disabled 状态用 `not-allowed`
- 阻止子元素任意覆盖

### 3. 移除 layout.tsx 的 cursor 设置

原来在 `htmlStyle` 里设置 `cursor: 'url(/images/cursor.svg) 2 1, auto'`，现在统一由 `globals.css` 管理，`layout.tsx` 只负责 CSS 变量桥接。

---

## 附带修复：导航卡片 Hover 高亮偏移

**问题**：`nav-card.tsx` 中"互动探索"标题导致后续项（发现/留言/关于）的 hover 高亮条位置偏移。

**原因**：标题占了一行视觉高度，但 `flatIndex` 和 `top` 计算没有考虑这个偏移。

**修复**：

```tsx
// flatIndex 加 1，给标题预留虚拟索引
const flatIndex = publicContentItems.length + 1 + index

// hover 动画 top 值补偿标题高度（约 28px）
animate={{
  top: hoveredIndex * (itemHeight + 4) + (hoveredIndex >= publicContentItems.length + 1 ? 28 : 0),
  left: 0,
  width: '100%',
  height: itemHeight
}}
```

---

## 遗留问题与改进方向

### 短期（P2）

- [ ] 标题高度补偿值（28px）是估算的，可能在不同字体/缩放下不精确
  - 改进：用 ref 测量标题实际高度，动态计算偏移
- [ ] 自定义鼠标在 Safari/Firefox 上的兼容性未验证

### 长期（P3 - 视觉系统重做后决定）

- [ ] **考虑移除自定义鼠标**：
  - 可访问性：系统鼠标对辅助技术更友好
  - 跨平台一致性：不同浏览器/OS 对自定义 cursor 的渲染有差异
  - 性能：SVG cursor 在某些场景下有轻微性能影响
  - 用户习惯：系统鼠标的 hover 状态变化是用户强依赖的视觉反馈

- [ ] 如果保留，需要：
  - 完整的 SVG cursor 集（pointer/text/grab/resize 等状态）
  - Dark mode 变体
  - 高 DPI 屏幕优化

---

## 影响范围

**Modified**:
- `src/app/layout.tsx` — 移除 cursor 设置，增加 CSS 变量桥接
- `src/components/nav-card.tsx` — 修正 hover 高亮计算
- `src/styles/globals.css` — 统一 cursor 继承策略
- `src/components/ui-v2/tokens.css` — 移除冲突的 cursor 规则（如有）

**Added**:
- `public/images/cursor-precise.svg` — 精准对齐的鼠标 SVG

**Deleted**:
- `src/styles/theme.css` — 已在之前清理（与本次无关）

---

## 测试建议

1. 在主页导航卡片上移动鼠标，验证 hover 高亮条精准对齐
2. 点击各导航项，验证点击位置与视觉箭头尖端一致
3. 在不同交互元素上移动鼠标，验证：
   - 普通内容区：自定义箭头
   - button/链接：系统 pointer
   - disabled 元素：系统 not-allowed
4. 验证不同浏览器（Chrome/Safari/Firefox）的兼容性
5. 验证不同屏幕缩放（100%/125%/150%）下的精准度

---

**参考对话**：`~/.claude/projects/-Users-limengyang-2025-blog-public/27f2df78-188e-4aee-8d92-d68a0efbcb7c.jsonl`
