# Evidence Baseline

**目的**：定义本文档所有事实性陈述的证据等级和验证方法，确保审计结果可追溯、可验证。

---

## 证据等级（Evidence Level）

### L1 — Verified（已验证）

**定义**：代码扫描 + 人工核实 + 运行时验证（三者至少满足两项）。

**示例**：
- 页面数量 = 53（`find src/app -name "page.tsx" | wc -l`）
- UI V2 组件数量 = 15（`ls -1 src/components/ui-v2/`）
- 路由使用 UI V2 = 0（`grep -r "import.*from '@/components/ui-v2" src/app`）

**验证方法**：
```bash
# 页面数量
find src/app -name "page.tsx" | wc -l

# UI V2 组件
ls -1 src/components/ui-v2/ | grep -E '\.(tsx|ts)$' | grep -v test

# 路由接入率
grep -r "import.*from '@/components/ui-v2" src/app --include="*.tsx" | wc -l
```

**更新频率**：每次 Phase 完成后重新验证。

---

### L2 — Static（静态分析）

**定义**：通过静态代码分析获得，未经运行时验证。

**示例**：
- 组件依赖图（import 关系）
- Token 定义位置（CSS 变量扫描）
- 组件 Props 接口（TypeScript 定义）

**验证方法**：
- TypeScript AST 分析
- 正则表达式扫描
- `grep`/`find` 组合

**局限性**：
- 无法识别动态导入（`dynamic import()`）
- 无法识别运行时条件渲染
- 无法验证实际渲染结果

**使用场景**：依赖关系分析、代码结构审计。

---

### L3 — Inferred（推断）

**定义**：从代码推断，需要运行时验证才能确认。

**示例**：
- 响应式覆盖情况（需浏览器验证）
- 色彩对比度（需工具测量）
- 键盘导航完整性（需手动测试）
- 性能指标（需 Lighthouse 或真机测试）

**标注方式**：在对应章节添加 `[需验证 L3]`。

**验证方法**：
- 浏览器 DevTools
- Lighthouse
- axe-core
- 真机测试

**风险**：推断结论可能与实际运行不符。

---

### L4 — Pending（待核实）

**定义**：文档编写时无法验证，需要后续补充。

**示例**：
- 某些 API 契约（需后端确认）
- 第三方服务集成细节（需配置文件或运维确认）
- 历史架构决策原因（需询问团队）

**标注方式**：在对应章节添加 `[待核实 L4 — 来源：XXX]`。

**处理流程**：
1. 记录待核实项
2. 标注预期来源
3. 后续补充后更新证据等级

---

## 验证方法分类

### 自动化验证

可在 CI/CD 中执行，结果稳定可复现。

| 类型 | 工具 | 输出 |
|------|------|------|
| **TypeScript 检查** | `npx tsc --noEmit` | 0 errors |
| **单元测试** | `npm test` | 通过率 |
| **组件测试** | Vitest | 覆盖率 |
| **构建验证** | `npm run build` | 成功/失败 |
| **静态扫描** | Shell 脚本 | 数量统计 |

---

### 半自动化验证

需要工具辅助，但需人工判断。

| 类型 | 工具 | 判断标准 |
|------|------|----------|
| **无障碍** | axe DevTools | 自动检测 + 人工复核 |
| **性能** | Lighthouse | Core Web Vitals |
| **视觉回归** | Percy/Chromatic | Diff 截图 |
| **色彩对比度** | Contrast Checker | WCAG AA 标准 |

---

### 人工验证

需要真人操作和判断。

| 类型 | 方法 | 验收标准 |
|------|------|----------|
| **键盘导航** | Tab/Shift+Tab 遍历 | 可达所有交互元素 |
| **屏幕阅读器** | VoiceOver/NVDA | 语义正确、顺序合理 |
| **真机测试** | iOS/Android | 布局正常、交互流畅 |
| **交叉浏览器** | Chrome/Safari/Firefox | 一致性 |

---

## 证据追溯格式

每项审计结论应包含以下字段：

```yaml
id: UI-AUDIT-001
category: component | layout | token | accessibility | performance
severity: P0 | P1 | P2 | P3
status: confirmed | inferred | pending
evidence_level: L1 | L2 | L3 | L4
source_files:
  - src/components/Button.tsx
finding: "存在重复的按钮样式定义"
evidence: |
  grep -r "className.*rounded-lg.*bg-" src/components | wc -l
  结果：34 处硬编码
impact:
  - maintainability
  - consistency
recommendation: "统一按钮变体与样式入口"
verification_method:
  - static_analysis
  - component_tests
verified_at: 2026-10-15
verified_by: automated_scan
```

---

## 更新流程

1. **Phase 执行前**：标注待验证项（L3/L4）
2. **Phase 执行中**：补充验证结果
3. **Phase 完成后**：
   - 更新证据等级（L3→L1，L4→L2）
   - 重新运行自动化验证
   - 记录验证时间和方法

---

## 约束

- **L3/L4 项不得作为 Phase 完成的唯一证据**
- **所有 P0 问题必须有 L1 证据支撑**
- **架构决策（ADR）必须有 L1/L2 证据基础**

---

**下一步**：在 `01-as-is/*` 和 `03-gap-analysis/*` 中应用本标准。
