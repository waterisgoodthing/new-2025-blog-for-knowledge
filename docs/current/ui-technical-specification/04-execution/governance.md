# Governance — 变更治理流程

**目的**：定义 UI 系统变更的审批、验证、发布和维护流程，确保长期一致性和质量。

---

## 1. 变更分类

### 1.1 Token 变更

**范围**：修改 `ui-v2/tokens.css` 中的任何 Token 值或定义

**审批**：
- **P0 Token**（brand/editorial-bg/admin-bg）：需产品负责人批准
- **P1 Token**（spacing/radius/shadow）：需技术负责人批准
- **新增 Token**：需设计 + 技术负责人批准

**影响分析**：
- 使用该 Token 的组件清单
- 受影响的页面清单
- 视觉回归范围

**验证**：
- Demo 页验证
- 受影响页面截图对比
- 色彩对比度验证（如涉及颜色）

---

### 1.2 组件变更

**范围**：修改 `src/components/ui-v2/` 中的任何组件

**审批**：
- **破坏性变更**（Props 接口改变）：需技术负责人批准
- **非破坏性变更**（内部实现、样式）：无需审批

**影响分析**：
- 使用该组件的页面清单
- 依赖该组件的其他组件

**验证**：
- 组件测试通过
- 使用该组件的页面功能回归
- axe-core 检测

---

### 1.3 Navigation 变更

**范围**：修改 PublicTopNav/AdminSidebar/MobileDrawer

**审批**：需技术负责人批准

**影响分析**：全站导航

**验证**：
- 全量功能回归测试
- 响应式验证
- 键盘导航验证

---

### 1.4 Overlay 变更

**范围**：修改 Modal/Drawer/ContextMenu/Popover

**审批**：需技术负责人批准

**影响分析**：
- 使用该 overlay 的功能清单

**验证**：
- 焦点管理验证
- axe-core 检测
- 键盘导航验证

---

## 2. 变更流程

### 2.1 提出变更

**步骤**：
1. 在 `tasks.md` 中创建新任务
2. 填写：
   - 变更范围
   - 变更原因
   - 影响分析
   - 验证计划
3. 标注优先级（P0/P1/P2）

**模板**：
```markdown
## [NEW] 任务名称

**变更范围**：修改 xxx
**变更原因**：解决 xxx 问题
**影响分析**：
- 受影响组件：xxx
- 受影响页面：xxx
**验证计划**：
- [ ] 组件测试
- [ ] 页面回归
- [ ] axe-core 检测
**优先级**：P1
**依赖**：无
```

---

### 2.2 审批流程

```
提出变更
    ↓
技术负责人审查
    ↓ (P0 Token)
产品负责人审查
    ↓
批准 / 拒绝
    ↓ (批准)
执行变更
```

**审批标准**：
- [ ] 变更必要性充分
- [ ] 影响分析完整
- [ ] 验证计划可行
- [ ] 无更优替代方案

**拒绝原因**：
- 影响范围过大且收益不明确
- 破坏现有设计原则
- 无法充分验证

---

### 2.3 执行变更

**步骤**：
1. 创建 feature branch：`git checkout -b feature/vsc-xx`
2. 实现变更
3. 本地验证（测试 + 构建）
4. 提交 commit（遵循 commit 规范）
5. 推送到远程

**Commit 规范**：
```
<type>(<scope>): <subject>

<body>

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
```

**Type**：
- `feat`: 新功能
- `fix`: 修复
- `refactor`: 重构
- `style`: 样式
- `test`: 测试
- `docs`: 文档

**Scope**：
- `token`: Token 系统
- `ui-v2`: UI V2 组件
- `nav`: Navigation
- `overlay`: Overlay 系统
- `a11y`: 无障碍

**示例**：
```
feat(token): add editorial warm surface tokens

- Add --editorial-bg, --editorial-surface, --editorial-accent
- Update tokens.css with complete editorial system
- Add demo page for token validation

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>
```

---

### 2.4 验证与合并

**验证清单**：
- [ ] TypeScript 0 errors
- [ ] 测试通过（前端 + 后端）
- [ ] 构建成功
- [ ] 功能回归通过
- [ ] axe-core 检测通过（如涉及 UI）
- [ ] 视觉验证通过（如涉及样式）

**合并流程**：
1. 验证完成后，合并到 `refactor/baseline`
2. 更新 `tasks.md` 状态为 `✅ 完成`
3. 记录验证结果

---

## 3. 版本管理

### 3.1 Token 系统版本

**版本号**：`<major>.<minor>.<patch>`

**版本策略**：
- **Major**：破坏性变更（Token 重命名、删除）
- **Minor**：新增 Token
- **Patch**：Token 值微调

**当前版本**：`1.0.0`（Phase 1 完成后）

**版本记录**：在 `ui-v2/tokens.css` 顶部记录：
```css
/**
 * UI V2 Token System
 * Version: 1.0.0
 * Last Updated: 2026-10-15
 * Changelog: Initial dual-surface system (editorial + admin)
 */
```

---

### 3.2 组件版本

**策略**：组件随项目版本，不单独版本化

**废弃流程**：
1. 标记 `@deprecated` 注释
2. 提供替代方案
3. 保留 1 个 Phase（约 1 个月）
4. 删除并清理引用

**示例**：
```tsx
/**
 * @deprecated Use UI V2 Modal instead. Will be removed in Phase 4.
 * @see src/components/ui-v2/Modal.tsx
 */
export function LegacyModal() { ... }
```

---

## 4. 文档维护

### 4.1 文档更新触发条件

| 触发条件 | 更新文档 | 更新人 |
|----------|----------|--------|
| Token 变更 | `design-foundations.md` + `token-systems.md` | 执行人 |
| 组件新增/修改 | `component-system.md` + `ui-inventory.md` | 执行人 |
| 架构变更 | `tech-stack.md` + `dependency-graph.md` | 技术负责人 |
| Phase 完成 | `refactoring-roadmap.md` + `tasks.md` | 执行人 |
| 技术债务新增 | `technical-debt.md` | 发现人 |

---

### 4.2 文档审查周期

**频率**：每个 Phase 完成后

**审查内容**：
- [ ] As-Is 文档与代码一致
- [ ] 证据等级准确
- [ ] 待核实项已补充
- [ ] 版本基线已更新

---

## 5. 质量门禁

### 5.1 Phase 门禁

**Phase 完成条件**：
- [ ] 所有任务状态为 `✅ 完成`
- [ ] 验收标准 100% 通过
- [ ] 文档已更新
- [ ] 技术负责人签字

**拒绝条件**（任一项触发）：
- TypeScript errors ≥ 1
- 测试 failed ≥ 1
- 构建失败
- axe-core critical issues ≥ 1
- 功能回归失败 ≥ 1 项

---

### 5.2 发布门禁

**发布到生产条件**：
- [ ] Phase 4 完成
- [ ] 全量功能回归测试通过
- [ ] Lighthouse Performance ≥ 90
- [ ] axe-core 0 critical issues（全站）
- [ ] 视觉回归验证通过
- [ ] 产品负责人批准

---

## 6. 回滚策略

### 6.1 Phase 级回滚

**触发条件**：
- 严重功能回归（阻断核心流程）
- 严重性能回退（Lighthouse < 70）
- 严重无障碍问题（axe-core critical ≥ 3）

**执行**：
```bash
# 回滚到 Phase N-1 完成状态
git revert <phase-n-commit-range>

# 或硬回滚
git reset --hard <phase-n-1-commit>
```

---

### 6.2 文件级回滚

**触发条件**：
- 单个文件变更引入问题
- 其他变更正常

**执行**：
```bash
# 回滚单个文件
git checkout <last-good-commit> -- <file-path>
git commit -m "revert: rollback <file-path> due to <reason>"
```

---

## 7. 技术债务管理

### 7.1 识别与记录

**触发条件**：
- 代码审查发现问题
- 用户反馈问题
- 无障碍检测发现问题
- 性能检测发现问题

**记录位置**：`technical-debt.md`

**记录格式**：
```markdown
## [D-XXX] 债务名称

**分类**：D1（视觉不一致）
**严重程度**：P1
**发现时间**：2026-10-15
**位置**：src/components/xxx
**描述**：xxx
**影响**：xxx
**修复建议**：xxx
**状态**：📋 待修复
```

---

### 7.2 偿还策略

**优先级**：
1. **P0**：阻断核心流程，立即修复
2. **P1**：影响体验，下个 Phase 修复
3. **P2**：轻微问题，后续优化

**偿还周期**：
- P0：当天
- P1：下个 Phase
- P2：下个大版本

---

## 8. 持续改进

### 8.1 回顾会议

**频率**：每个 Phase 完成后

**参与人**：技术负责人 + 执行人

**议题**：
- 本 Phase 完成情况
- 验收标准是否合理
- 流程是否需要优化
- 技术债务是否可控

---

### 8.2 指标跟踪

**跟踪指标**：

| 指标 | 目标 | 当前 |
|------|------|------|
| **Token 系统数量** | 1 套 | 3 套 → 1 套 ✅ |
| **UI V2 接入率** | 100% | 0% → 目标 100% |
| **axe-core critical** | 0 | 待测 → 0 |
| **Lighthouse Performance** | ≥ 90 | 待测 → ≥ 90 |
| **技术债务数量** | 减少 | 待盘点 → 减少 |

---

## 9. 权限与角色

| 角色 | 权限 | 责任 |
|------|------|------|
| **产品负责人** | P0 Token 审批、发布审批 | 产品方向 |
| **技术负责人** | 所有变更审批、Phase 签字 | 技术方向、质量把控 |
| **执行人** | 提出变更、执行变更、更新文档 | 实现与验证 |
| **用户** | 反馈问题 | 提供体验反馈 |

---

## 10. 紧急情况处理

### 10.1 生产故障

**定义**：生产环境功能不可用

**流程**：
1. 立即回滚到上一稳定版本
2. 分析根本原因
3. 修复并验证
4. 重新发布

---

### 10.2 安全问题

**定义**：发现安全漏洞或隐私泄露

**流程**：
1. 立即评估影响范围
2. 修复并验证
3. 紧急发布（跳过正常流程）
4. 通知相关方

---

**更新日志**：
- 2026-10-15：初始版本
