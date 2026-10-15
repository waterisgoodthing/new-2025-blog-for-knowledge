# 系统收敛工作空间

创建日期：2026-10-13  
基线：refactor/baseline @ 4a954eaa  
模式：WORKER（主智能体 + Haiku 子智能体团队）

## 目标与范围

基于 [ARCHITECTURE_AUDIT](../../audits/ARCHITECTURE_AUDIT.md) 和 [DESIGN_RATIONALE_REVIEW](../../architecture/DESIGN_RATIONALE_REVIEW.md) 的分析，建立一个**系统性解决架构偏移与设计缺口**的执行框架。

### 核心目标

**不是**解决单个测试文件的类型错误，而是：

1. **统一数据合同**：KP 双轨写协议、AI 确认快照、来源审计
2. **闭合学习链路**：题目 → 错题 → 复习 → 统计 → 练习的完整性
3. **建立运行基线**：前后端分离验证、真实浏览器流程、数据库一致性
4. **视觉体验达标**：八维质量标准、三条关键流程、响应式与可访问性

### 当前系统状态（来自审查）

| 维度 | 状态 | 主要问题 |
|------|------|---------|
| 架构成熟度 | PARTIAL | MVP 能力骨架存在，运行可用性未验证 |
| 数据合同 | CONFIRMED_DRIFT | A04 KP 双轨、A05-A06 长度/枚举偏移 |
| AI 治理 | CONFIRMED_DRIFT / HIGH | A01-A03 来源/快照/并发缺口 |
| 前端体验 | NOT_VERIFIED | 视觉质量未测、加载阻断、交互身份隔离不足 |
| 测试门禁 | FAIL | A13 类型检查、完整 E2E 未执行 |
| 生产就绪 | BLOCKED | A15 运行验收不足 |

## 执行策略

### 阶段划分（按 ROADMAP.md）

```
Phase 1: 基线保护与类型门禁 (N00-N01)
  ↓
Phase 2: 数据合同收敛 (N02-N03)
  ↓
Phase 3: 前端体验与交互 (N04 + 视觉迭代)
  ↓
Phase 4: 完整验收 (N06)
  ↓
Phase 5: 前后端联合检查（强制派遣子智能体）
```

### 角色分离机制

**主智能体（Opus 5.5）**：
- 总体设计决策
- 跨域边界裁决
- 用户沟通
- 最终代码接受

**前端专家（Haiku）**：
- React/Next.js 实现
- UI/UX 质量检查
- 浏览器兼容性验证

**后端专家（Haiku）**：
- FastAPI/SQLAlchemy 实现
- 数据库合同验证
- API 一致性检查

**独立审查者（Haiku）**：
- 代码审查（不参与实施）
- 设计合理性质疑
- 风险识别

**验证者（Haiku）**：
- 测试执行
- 证据收集
- 环境隔离验证

## 核心原则

### 1. 证据驱动决策

**每个 "已修复" 必须有**：
- 修复前的问题复现（命令 + 输出）
- 修复后的验证证据（测试通过 + 新事务回读）
- 独立审查批准
- 主智能体最终接受

**禁止**：
- "理论上应该工作"
- "看起来没问题"
- "之前测试通过了"（不复现当前状态）

### 2. 架构完整性优先

**修复顺序**：
1. 数据合同（DR-B01, DR-B02）- 影响所有后续功能
2. 核心链路（学习闭环）- 业务价值基础
3. 交互体验（N04 + 视觉）- 用户可感知质量
4. 边缘情况（A07-A10）- 细化语义

**不允许**：
- 为了快速"通过测试"而绕过真实问题
- 局部修复导致其他模块不一致
- 只改文档不改代码（除非是纯文档问题）

### 3. 前后端分离验证

**后端验证（独立于前端）**：
- 纯 HTTP 测试（curl/pytest）
- 数据库约束测试
- 并发竞争测试
- 事务回滚测试

**前端验证（独立于后端）**：
- Mock API 的 UI 状态测试
- 键盘/触控流程
- 响应式布局
- 可访问性检查

**集成验证（联合）**：
- 真实浏览器 + 真实 API
- 三条关键流程端到端
- 迟到响应、乱序、竞态条件

### 4. 增量可验收

**每个子任务退出条件**：
- 明确的验收标准（AC-001, AC-002...）
- 可重现的验证命令
- 独立审查 APPROVE
- 相关测试全部 PASS
- Git diff 可追溯

**状态定义**：
- `COMPLETE`: 所有 AC 通过 + 独立审查 APPROVE
- `PARTIAL`: 部分通过，明确剩余问题
- `BLOCKED`: 依赖或风险阻断，需要决策
- `FAILED`: 验证失败，需要返工

## 工作空间结构

```
system-convergence-workspace/
├── README.md                    # 本文件
├── requirements.md              # 完整需求与验收矩阵
├── design.md                    # 架构修复方案
├── tasks.md                     # 任务分解与依赖
├── validation.md                # 验证策略
├── phase1-baseline/             # N00-N01 基线与类型
│   ├── tasks.md
│   ├── evidence/
│   └── acceptance.md
├── phase2-contracts/            # N02-N03 数据合同
│   ├── tasks.md
│   ├── evidence/
│   └── acceptance.md
├── phase3-experience/           # N04 + 视觉体验
│   ├── tasks.md
│   ├── evidence/
│   └── acceptance.md
├── phase4-acceptance/           # N06 完整验收
│   ├── tasks.md
│   ├── evidence/
│   └── acceptance.md
└── phase5-integration/          # 前后端联合检查
    ├── backend-verification.md
    ├── frontend-verification.md
    ├── integration-tests.md
    └── final-report.md
```

## Phase 5: 强制前后端联合检查

**这是工作空间的强制退出门禁**，不可跳过。

### 后端独立验证（Haiku Backend Expert）

**必须完成**：
1. 数据库 Schema 一致性
   - Alembic 迁移图完整
   - ORM 模型与 DB 定义一致
   - 约束、索引、FK 验证
   
2. API 合同测试
   - 所有 router 端点可达
   - Schema 验证（request/response）
   - 错误状态码一致
   
3. 业务不变量测试
   - KP 关系单一写协议
   - AI 确认原子性
   - 复习调度正确性
   - 并发竞争保护

4. 数据持久化验证
   - 新事务读回验证
   - 回滚测试
   - 外键级联正确性

### 前端独立验证（Haiku Frontend Expert）

**必须完成**：
1. 组件状态隔离
   - 异步状态正确处理
   - 迟到响应不污染新状态
   - 切换时清理旧请求
   
2. 用户交互完整性
   - 三条关键流程全覆盖
   - 键盘导航可用
   - 触控目标 ≥44px
   
3. 视觉质量达标
   - 八维标准检查
   - 390/768/1440 响应式
   - reduced-motion 支持
   
4. 可访问性基线
   - ARIA 标签完整
   - 焦点管理正确
   - 读屏器测试（至少一个）

### 集成验证（Independent Verifier）

**必须完成**：
1. 真实浏览器 E2E
   - Dashboard → Review → 再答 → 记录查询
   - Capture → 人工确认 → 草稿转换 → 正式确认
   - Notes → 编辑 → 保存 → 新请求回读
   
2. 竞态条件测试
   - 双会话并发确认
   - 迟到响应覆盖保护
   - 切换实体后响应隔离
   
3. 错误处理完整性
   - 网络失败重试
   - 服务端错误显示
   - 数据验证失败提示

### 联合检查报告模板

```yaml
integration_verification:
  date: YYYY-MM-DD
  backend_expert_id: <agent_id>
  frontend_expert_id: <agent_id>
  verifier_id: <agent_id>
  primary_owner: opus-5.5
  
  backend_verification:
    schema_consistency: PASS/FAIL
    api_contracts: PASS/FAIL
    business_invariants: PASS/FAIL
    data_persistence: PASS/FAIL
    evidence_files: [...]
    blocking_issues: [...]
  
  frontend_verification:
    component_isolation: PASS/FAIL
    user_interactions: PASS/FAIL
    visual_quality: PASS/FAIL
    accessibility: PASS/FAIL
    evidence_files: [...]
    blocking_issues: [...]
  
  integration_tests:
    e2e_flows: PASS/FAIL
    race_conditions: PASS/FAIL
    error_handling: PASS/FAIL
    evidence_files: [...]
    blocking_issues: [...]
  
  independence_verified: true
  cross_contamination_check: PASS
  
  final_decision: ACCEPT/PARTIAL/REJECT
  
  summary: |
    简短总结前后端各自状态、集成测试结果、
    剩余问题和是否满足发布基线。
```

## 防自编自演机制

**强制要求**：
1. 后端实施者 ≠ 后端审查者 ≠ 后端验证者
2. 前端实施者 ≠ 前端审查者 ≠ 前端验证者
3. 集成验证者不参与前后端实施
4. 主智能体复核关键证据，不盲目接受

**证据链追踪**：
- 每个 agent 的 ID 记录在案
- 每个决策的证据文件路径
- 每个测试的命令和输出
- 每个审查意见的处理记录

## 成功退出条件

**系统级**：
- A01-A06（HIGH 级问题）全部闭合
- A13 类型检查 PASS
- N02-N04 验收通过
- N06 原计划验收达标

**质量级**：
- 后端独立验证 PASS
- 前端独立验证 PASS
- 集成测试 PASS
- 独立审查批准

**文档级**：
- 所有决策有记录
- 所有证据可追溯
- 剩余问题明确列出
- 下一步建议清晰

## 阻断条件

**立即停止**：
- 发现数据丢失风险
- 发现安全漏洞
- 需要修改认证机制（G3）
- 需要生产数据迁移（G2 + G5）

**上报用户决策**：
- 需要改变产品语义（G0）
- 需要架构重构（G1）
- 预算超出预期
- 依赖外部服务

## 与原计划的关系

本工作空间**执行** ROADMAP.md 中的 N00-N06 路线：
- N00: 基线保护
- N01: 类型门禁
- N02: AI 合同
- N03: KP 合同
- N04: 交互修复
- N06: 完整验收

**不改变**：
- 原 Week/PR 验收标准
- 历史 Gate 记录
- B07 退出条件

**补充**：
- 强制前后端分离验证
- 视觉质量标准
- 证据链完整性要求

## 时间与成本估算

**保守估计**（基于审查发现的问题规模）：
- Phase 1: 2-3 天（基线 + 类型修复）
- Phase 2: 5-7 天（数据合同收敛）
- Phase 3: 7-10 天（交互 + 视觉迭代）
- Phase 4: 3-5 天（完整验收）
- Phase 5: 2-3 天（联合检查）
- **总计**: 19-28 天（纯执行时间，不含等待审批）

**实际时间可能因以下因素延长**：
- 发现新的架构问题
- 需要用户决策
- 测试环境问题
- 外部依赖阻断

## 下一步

等待用户确认：
1. **是否接受此工作空间定义**？
2. **是否授权开始 Phase 1（N00-N01）**？
3. **是否有预算或时间约束**？
4. **是否有特定优先级调整**？

确认后，我将：
1. 创建详细的 requirements.md
2. 创建 design.md（架构修复方案）
3. 创建 phase1-baseline/ 目录和任务
4. 派遣 Haiku 子智能体开始调查
5. 开始执行 N00（基线锁定）
