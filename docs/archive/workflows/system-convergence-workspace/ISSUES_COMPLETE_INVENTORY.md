# 架构问题完整清单

## 元数据

**创建时间**: 2026-10-13  
**最后更新**: 等待深度分析完成  
**状态**: 🟡 收集中

---

## 已识别问题分类

### P0 - 阻断发布（必须修复）

| ID | 问题 | 来源 | 状态 | 工作空间覆盖 |
|---|---|---|---|---|
| A01 | AI 输入来源校验缺失 | ARCHITECTURE_AUDIT | 🔴 待修复 | ✅ Phase 2 |
| A02 | AI 确认快照缺失 | ARCHITECTURE_AUDIT | 🔴 待修复 | ✅ Phase 2 |
| A03 | AI 并发协议缺失 | ARCHITECTURE_AUDIT | 🔴 待修复 | ✅ Phase 2 |
| A04 | KP 双轨写协议不一致 | ARCHITECTURE_AUDIT | 🔴 待修复 | ✅ Phase 2 |
| A13 | TypeScript 类型检查 FAIL | ARCHITECTURE_AUDIT | 🔴 待修复 | ✅ Phase 1 |
| A15 | 完整运行验收未完成 | ARCHITECTURE_AUDIT | 🔴 待修复 | ✅ Phase 4 |
| ENV-001 | 数据库环境混淆 | 深度调查 | 🔴 待修复 | ✅ Phase 1 |
| DESIGN-004 | 页面加载阻断 | DESIGN_RATIONALE | 🔴 待修复 | ✅ Phase 3 |

### P1 - 核心功能（高优先）

| ID | 问题 | 来源 | 状态 | 工作空间覆盖 |
|---|---|---|---|---|
| A05 | 输入合同长度不一致 | ARCHITECTURE_AUDIT | 🟡 待修复 | ✅ Phase 2 |
| A06 | 枚举偏移不一致 | ARCHITECTURE_AUDIT | 🟡 待修复 | ✅ Phase 2 |
| A07 | 历史归因缺失版本快照 | ARCHITECTURE_AUDIT | 🟡 待修复 | ✅ Phase 2 |
| A08 | 归档生命周期设计缺口 | ARCHITECTURE_AUDIT | 🟡 待修复 | ✅ Phase 2 |
| A11 | Capture 状态身份隔离 | ARCHITECTURE_AUDIT | 🟡 待修复 | ✅ Phase 3 |
| A12 | Notes 列表分页 | ARCHITECTURE_AUDIT | 🟡 待修复 | ✅ Phase 3 |
| ENV-002 | 测试数据库管理混乱 | 深度调查 | 🟡 待修复 | ✅ Phase 1 |
| ENV-003 | 生产保护不足 | 深度调查 | 🟡 待修复 | ✅ Phase 1 |
| DESIGN-001 | 设计系统未统一（两套并存）| 深度调查 | 🟡 待修复 | ✅ Phase 3 |
| DESIGN-002 | UI V2 组件未挂载 | UI_V2_TRACKER | 🟡 待修复 | ✅ Phase 3 |

### P2 - 质量改进（可延后）

| ID | 问题 | 来源 | 状态 | 工作空间覆盖 |
|---|---|---|---|---|
| A09 | 合同字段不必要可选 | ARCHITECTURE_AUDIT | 🟢 待评估 | ✅ Phase 2 |
| A10 | 枚举定义重复 | ARCHITECTURE_AUDIT | 🟢 待评估 | ✅ Phase 2 |
| A14 | 视觉体验迭代空间 | ARCHITECTURE_AUDIT | 🟢 待评估 | ✅ Phase 3 |
| DESIGN-003 | 八维视觉标准未验证 | DESIGN_RATIONALE | 🟢 待评估 | ✅ Phase 3 |

---

## 快速扫描新增问题（待整合）

### 安全相关

| ID | 问题 | 严重程度 | 证据 |
|---|---|---|---|
| SCAN-S01 | 认证覆盖不完整 | 🟡 MEDIUM | 35/36 路由有认证，1 个可能缺失 |
| SCAN-S02 | XSS 风险点未验证 | 🟡 MEDIUM | 7 处 dangerouslySetInnerHTML |
| SCAN-S03 | 前端凭证处理不一致 | 🟡 MEDIUM | credentials: 'include' 混合使用 |
| SCAN-S04 | 级联删除风险 | 🟡 MEDIUM | 15+ ondelete="CASCADE" 无保护 |

### 代码质量

| ID | 问题 | 严重程度 | 证据 |
|---|---|---|---|
| SCAN-Q01 | 调试代码残留 | 🟢 LOW | 31 console.log + 2 print() |
| SCAN-Q02 | 错误处理过于宽泛 | 🟡 MEDIUM | 11 个 except Exception |
| SCAN-Q03 | 临时文件未清理 | 🟢 LOW | backend_server.log + 10+ playwright logs |

### 性能与扩展

| ID | 问题 | 严重程度 | 证据 |
|---|---|---|---|
| SCAN-P01 | 分页缺失 | 🟡 MEDIUM | Notes/Mistakes/Questions 无分页 |
| SCAN-P02 | 索引覆盖未验证 | 🟡 MEDIUM | 65 索引 vs 70 外键 |

### 运维与部署

| ID | 问题 | 严重程度 | 证据 |
|---|---|---|---|
| SCAN-O01 | 后端 CI 缺少 lint | 🟡 MEDIUM | CI 注释："no ruff/mypy... would fail" |
| SCAN-O02 | 备份策略未验证 | 🟡 MEDIUM | 有文档但无实际运行证据 |

---

## 深度分析新增问题（已完成）✅

**状态**: ✅ 报告完成（2026-10-13）

### CRITICAL 级别（4个）

#### NEW-C01: Session State Leakage Risk Across Concurrent Requests
- **严重程度**: CRITICAL
- **分类**: security/concurrency
- **描述**: AUTH_BYPASS 状态在请求间可能不一致，session 固定/权限提升风险
- **证据**:
  - `backend/app/database.py:16-23` 请求级提交/回滚
  - `backend/app/routers/auth.py:84-89` AUTH_BYPASS 实时检查不缓存
  - `src/lib/api/client.ts:90` credentials: 'include' 全局使用
- **影响**: 环境变量在部署时变化可能导致会话状态不一致，多实例下不同授权决策
- **风险**: Session fixation, privilege escalation

#### NEW-C02: No Transaction Isolation Level Control
- **严重程度**: CRITICAL
- **分类**: data/concurrency
- **描述**: 未设置事务隔离级别，默认 READ COMMITTED，存在丢失更新、幻读风险
- **证据**:
  - `backend/app/database.py:8` create_engine 无 isolation_level
  - `backend/app/services/review_item_service.py:64` 使用 with_for_update() 但事务隔离未保证
  - 仅 11 处行级锁
- **影响**: 多步骤业务逻辑（KP 统计、复习调度）可能数据损坏
- **风险**: Lost updates, phantom reads, write skew anomalies

#### NEW-C03: No Database Connection Pool Configuration
- **严重程度**: CRITICAL
- **分类**: performance/reliability
- **描述**: 未配置连接池参数，默认 5 个连接
- **证据**: `backend/app/database.py:8` 无 pool_size, max_overflow, pool_recycle, pool_timeout
- **影响**: >5 并发请求时阻塞，无连接回收导致积压，无超时可能无限挂起
- **风险**: Service degradation, connection exhaustion, cascading failures

#### NEW-C04: Blind Cascade Delete Without Orphan Protection
- **严重程度**: CRITICAL
- **分类**: data/integrity
- **描述**: 多处 CASCADE 删除无补偿保护
- **证据**:
  - `admin_sessions.user_id` CASCADE
  - `admin_profile.user_id` CASCADE
  - `attachment_links` CASCADE
  - `note_versions` CASCADE
- **影响**: 删除 User 级联到 AdminSessions，但应用层未撤销活跃会话
- **风险**: Zombie sessions, audit trail breaks, orphaned resources

---

### HIGH 级别（7个）

#### NEW-H01: No Index on Critical Time-Range Queries
- **分类**: performance
- **证据**: `Attempt.submitted_at`, `AiRun.created_at`, `AuditLog` 无时间范围索引，仅 26 个索引定义
- **影响**: Dashboard "recent" 查询、AI 历史、审计日志浏览将全表扫描
- **建议**: 添加 `attempts(submitted_at)`, `ai_runs(created_at)`, `audit_logs(created_at)` 索引

#### NEW-H02: No Query Timeout or Statement Timeout
- **分类**: performance/reliability
- **证据**: 无 statement_timeout 配置，无查询超时包装
- **影响**: 失控查询（缺少 WHERE、错误 join）可能无限占用连接
- **风险**: Single slow query blocks entire pool

#### NEW-H03: Attempt Model Missing Question Version Snapshot
- **分类**: data/historical-accuracy
- **证据**:
  - `backend/app/models/attempt.py:14-15` 仅存储 question_id 和 submitted_answer，无 question_version
  - `backend/app/models/mistake.py:69-70` MistakeDraft 有快照但 Attempt 没有
- **影响**: Question 内容变化后，历史 Attempt.is_correct 无法验证，练习统计混合新旧版本
- **风险**: Cannot audit "why was this marked correct"

#### NEW-H04: No Frontend Request Deduplication
- **分类**: performance/correctness
- **证据**:
  - SWR 使用但无 dedupingInterval 配置
  - `src/app/manage/(workspace)/dashboard/dashboard-content.tsx:14-18` 分别获取 dashboard+profile
- **影响**: 快速导航/重试触发重复请求，无批量优化
- **风险**: Wasted resources, stale data flash, double-submit

#### NEW-H05: AI Run Status Not Indexed
- **分类**: performance
- **证据**: A02 指出 ai_run.py 缺确认快照，且无 status 索引
- **影响**: `/api/admin/ai/runs` 按状态过滤需全表扫描
- **建议**: 添加 `idx_ai_runs_status_created` 复合索引

#### NEW-H06: No CSRF Protection Beyond SameSite
- **分类**: security
- **证据**: `backend/app/routers/auth.py:44,58-60` 仅 samesite="lax"，无 CSRF token
- **影响**: SameSite=Lax 允许顶级导航发送 cookie，恶意站点可构造表单提交
- **风险**: One-click account takeover if victim visits attacker site while logged in

#### NEW-H07: Unbounded Growth of Audit Logs and AI Runs
- **分类**: operations/cost
- **证据**: 无保留策略、归档、分区策略
- **影响**: audit_logs 和 ai_runs 表无限增长，治理查询变慢
- **建议**: 时间分区或定期归档

---

### MEDIUM 级别（6个）

#### NEW-M01: No Structured Logging with Correlation IDs
- **分类**: operations
- **证据**: auth.py 有 logger.warning 但无 request_id、session_id 传播
- **影响**: 无法关联前端错误与后端日志，无法追踪多步骤失败

#### NEW-M02: Weak Error Messages Leak Internal State
- **分类**: security/user-experience
- **证据**: 多处服务返回原始异常（如 "Knowledge point not found" 泄露存在性）
- **影响**: 时序攻击已通过限流缓解，但详细错误帮助侦查

#### NEW-M03: No Health Check Exposes Database Status
- **分类**: operations
- **证据**: `backend/app/config.py:57` 提到 /api/health 但无对应端点
- **影响**: 负载均衡器无法区分"应用运行但 DB 挂"和"应用健康"

#### NEW-M04: Frontend Error Boundaries Not Comprehensive
- **分类**: user-experience/reliability
- **证据**: dashboard-content.tsx:36-38 有错误状态，但无 React ErrorBoundary 包装路由段
- **影响**: 未处理渲染错误导致整个工作区崩溃而非显示降级 UI

#### NEW-M05: No Explicit API Versioning Strategy
- **分类**: maintainability
- **证据**: 所有路由在 /api/admin/* 下，无 /v1/ 前缀或版本头
- **影响**: 未来破坏性变更需要 URL 更改或复杂协商

#### NEW-M06: AsyncStatePanel Used Inconsistently
- **分类**: user-experience/maintainability
- **证据**: Dashboard 使用 AsyncStatePanel，其他工作区页面可能内联加载检查
- **影响**: 不一致错误 UX，重复重试逻辑

---

### 反模式识别

#### Pattern: Implicit Default Values in Business Logic
- **出现次数**: 8+ 处
- **示例**:
  - review_item_service.py 硬编码间隔 `{0:1, 1:1, 2:2}`
  - config.py 多处默认值嵌入类定义
  - 无中心化常量文件
- **风险**: 更改学习算法需要源码修改，无法 A/B 测试或用户定制

#### Pattern: Mixed Old/New Field Pairs Without Migration Plan
- **出现次数**: A04/A02/A05
- **风险**: 无系统化双写审计工具，无记录的切换标准

#### Pattern: Weak Foreign Key Referential Actions
- **出现次数**: 20+ RESTRICT
- **风险**: 无法清理归档 Questions，因为 Attempts 阻止删除，无垃圾回收策略

#### Pattern: No Prepared Statement Caching Evidence
- **风险**: 每个相同查询重新编译 SQL，浪费 CPU

---

### 交叉观察

1. **无分布式追踪**: 447 个 TS 文件，37 个路由，36 个迁移，但无 OpenTelemetry
2. **无背压机制**: AI 提供商慢时请求堆积，无 503 熔断器
3. **无数据库迁移回滚测试**: 36 个迁移但 rollback NOT_VERIFIED
4. **无上传内容类型验证**: 附件服务检查大小但无 MIME 验证，多语言文件利用风险
5. **SWR 缓存不按会话分区**: 登出后新用户可能看到旧会话缓存

---

## 问题统计（已更新）

### 按优先级

- **P0（阻断）**: 8 个（原有）+ 4 个（NEW-C01-C04）= **12 个**
- **P1（高优先）**: 10 个（原有）+ 7 个（NEW-H01-H07）= **17 个**
- **P2（可延后）**: 4 个（原有）+ 6 个（NEW-M01-M06）= **10 个**
- **快速扫描**: 11 个（待分类整合）
- **反模式**: 4 个识别

**总计**: **54+ 个已识别问题**

### 按分类

#### 安全问题（11个）
- NEW-C01: Session state leakage (CRITICAL)
- NEW-H06: No CSRF protection (HIGH)
- NEW-M02: Error message leaks (MEDIUM)
- SCAN-S01: 认证覆盖不完整 (MEDIUM)
- SCAN-S02: XSS 风险点 (MEDIUM)
- SCAN-S03: 凭证处理不一致 (MEDIUM)
- SCAN-S04: 级联删除风险 (MEDIUM)
- 其他（A01-A03 AI 安全相关）

#### 数据一致性（8个）
- NEW-C02: 无事务隔离控制 (CRITICAL)
- NEW-C04: CASCADE 无保护 (CRITICAL)
- NEW-H03: Attempt 缺版本快照 (HIGH)
- A04: KP 双轨不一致 (P0)
- A07: 历史归因缺快照 (P1)
- A08: 归档生命周期缺口 (P1)
- 其他数据合同问题

#### 性能问题（8个）
- NEW-C03: 无连接池配置 (CRITICAL)
- NEW-H01: 时间范围无索引 (HIGH)
- NEW-H02: 无查询超时 (HIGH)
- NEW-H04: 前端无去重 (HIGH)
- NEW-H05: AI Run 状态无索引 (HIGH)
- NEW-H07: 审计日志无界增长 (HIGH)
- SCAN-P01: 分页缺失 (MEDIUM)
- SCAN-P02: 索引覆盖未验证 (MEDIUM)

#### 运维与监控（5个）
- NEW-M01: 无结构化日志 (MEDIUM)
- NEW-M03: 无健康检查 (MEDIUM)
- SCAN-O01: 后端 CI 缺 lint (MEDIUM)
- SCAN-O02: 备份未验证 (MEDIUM)
- 其他部署相关

#### 用户体验（7个）
- DESIGN-004: 页面加载阻断 (P0)
- DESIGN-001: 设计系统未统一 (P1)
- DESIGN-002: UI V2 未挂载 (P1)
- NEW-M04: Error Boundary 不完整 (MEDIUM)
- NEW-M06: AsyncStatePanel 不一致 (MEDIUM)
- A11-A12: Capture/Notes 交互 (P1)
- A14: 视觉体验迭代 (P2)

#### 代码质量（6个）
- A13: TypeScript 类型 FAIL (P0)
- SCAN-Q01: 调试代码残留 (LOW)
- SCAN-Q02: 错误处理过宽 (MEDIUM)
- SCAN-Q03: 临时文件未清理 (LOW)
- NEW-M05: 无 API 版本策略 (MEDIUM)
- 反模式 4 个

### 按状态

- 🔴 **CRITICAL（必须修复）**: 4 个（NEW-C01-C04）
- 🔴 **P0（阻断发布）**: 8 个（A01-A03, A04, A13, A15, ENV-001, DESIGN-004）
- 🟡 **HIGH（高优先）**: 7 个（NEW-H01-H07）
- 🟡 **P1（尽快修复）**: 10 个（A05-A08, A11-A12, ENV-002-003, DESIGN-001-002）
- 🟢 **MEDIUM（规划修复）**: 6 个（NEW-M01-M06）
- 🟢 **P2（可延后）**: 4 个（A09-A10, A14, DESIGN-003）
- ⚪ **LOW（优化）**: 3 个（SCAN-Q01, Q03）
- 📊 **待分类**: 8 个快速扫描项

### 工作空间覆盖

- ✅ **已纳入**: 22 个（A01-A15 + ENV + DESIGN）
- 🆕 **需新增 Phase 1 任务**: NEW-C02, NEW-C03（数据库基础设施）
- 🆕 **需新增 Phase 2 任务**: NEW-C01, NEW-C04, NEW-H03（数据合同与安全）
- 🆕 **需新增 Phase 3 任务**: NEW-M04, NEW-M06（前端体验）
- 🆕 **需新增 Phase 4 任务**: NEW-H01-H07, NEW-M01-M05（性能与运维）
- 🆕 **需新增 Phase 5 验证**: 安全审查、性能基线、运维就绪

---

## 下一步行动

### 等待深度报告完成后

1. **整合所有发现**
   - 合并重复问题
   - 分类新问题
   - 确定优先级

2. **更新工作空间**
   - requirements.md: 新增需求
   - validation.md: 新增验证项
   - tasks.md: 分配任务

3. **重新评估时间**
   - Phase 1-5 时间可能延长
   - 识别快速修复项
   - 识别可延后项

4. **向用户报告**
   - 完整问题清单
   - 影响评估
   - 建议执行顺序

---

**此文档将在深度分析完成后更新为最终版本。**
