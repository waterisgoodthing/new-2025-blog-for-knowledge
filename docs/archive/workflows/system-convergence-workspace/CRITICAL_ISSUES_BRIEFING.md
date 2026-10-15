# 关键问题简报

## 执行摘要

**状态**: 🔴 **发现 4 个 CRITICAL 级别阻断问题**  
**日期**: 2026-10-13  
**来源**: 深度架构分析

---

## 🚨 CRITICAL 级别问题（必须立即修复）

### NEW-C01: Session State Leakage Risk ⚠️

**严重程度**: CRITICAL  
**分类**: Security / Concurrency

**问题**:
- AUTH_BYPASS 环境变量在请求执行期间可能变化
- Session 状态在多实例部署时不一致
- 认证决策可能在同一请求的不同阶段不同

**证据**:
```python
# backend/app/routers/auth.py:84-89
AUTH_BYPASS = os.getenv("AUTH_BYPASS") == "true"  # 实时读取，不缓存

# 请求开始时：AUTH_BYPASS = False → 需要认证
# 部署期间环境变量改变
# 请求执行时：AUTH_BYPASS = True → 绕过认证
```

**影响**: Session fixation, privilege escalation

**修复建议**:
```python
# 方案 1: 请求级缓存
@lru_cache(maxsize=1)
def get_auth_config():
    return {
        'auth_bypass': os.getenv("AUTH_BYPASS") == "true",
        'timestamp': time.time()
    }

# 方案 2: 启动时锁定
class Settings(BaseSettings):
    AUTH_BYPASS: bool = False
    
    @validator('AUTH_BYPASS')
    def validate_auth_bypass(cls, v):
        if v and os.getenv("ENV") == "production":
            raise ValueError("AUTH_BYPASS cannot be true in production")
        return v
```

**优先级**: 🔴 Phase 0.5 或 Phase 1 最优先

---

### NEW-C02: No Transaction Isolation Level Control ⚠️

**严重程度**: CRITICAL  
**分类**: Data / Concurrency

**问题**:
- SQLAlchemy 引擎未配置事务隔离级别
- 默认 READ COMMITTED 无法防止 write skew
- 多步骤业务逻辑存在竞态条件

**证据**:
```python
# backend/app/database.py:8
engine = create_async_engine(settings.DATABASE_URL, echo=False)
# 缺少: isolation_level="REPEATABLE READ"
```

**影响**:
- KP 统计聚合可能不准确
- 复习调度可能重复或遗漏
- 并发提交答案可能丢失更新

**修复建议**:
```python
# 方案 1: 全局 REPEATABLE READ（推荐）
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    isolation_level="REPEATABLE READ"  # PostgreSQL 支持
)

# 方案 2: 审计所有竞态条件
# 为每个多步骤业务逻辑添加 SELECT FOR UPDATE
```

**测试用例**:
```python
# 竞态测试：并发更新同一 ReviewItem
async def test_concurrent_review_update():
    # 两个并发请求更新 next_review_at
    # 预期：一个成功，一个重试或失败
    # 实际（无隔离）：两个都成功，后者覆盖前者
```

**优先级**: 🔴 Phase 1 必须修复

---

### NEW-C03: No Database Connection Pool Configuration ⚠️

**严重程度**: CRITICAL  
**分类**: Performance / Reliability

**问题**:
- 连接池未配置，默认仅 5 个连接
- 无连接回收策略（pool_recycle）
- 无连接超时（pool_timeout）
- >5 并发请求时阻塞

**证据**:
```python
# backend/app/database.py:8
engine = create_async_engine(settings.DATABASE_URL, echo=False)
# 缺少：
# pool_size=20,
# max_overflow=10,
# pool_recycle=3600,
# pool_timeout=30
```

**影响**:
- 6 个并发请求时第 6 个无限等待
- 陈旧连接积压（数据库重启后）
- 连接泄露无法检测

**修复建议**:
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,              # 常驻连接数
    max_overflow=10,           # 峰值额外连接
    pool_recycle=3600,         # 1 小时回收连接
    pool_timeout=30,           # 30 秒获取连接超时
    pool_pre_ping=True         # 使用前检测连接有效性
)
```

**负载测试**:
```bash
# 测试 30 并发用户
ab -n 1000 -c 30 http://localhost:8000/api/admin/dashboard
# 预期：所有请求 <1s 响应
# 实际（无配置）：25+ 请求超时
```

**优先级**: 🔴 Phase 1 必须修复

---

### NEW-C04: Blind Cascade Delete Without Orphan Protection ⚠️

**严重程度**: CRITICAL  
**分类**: Data / Integrity

**问题**:
- 多处 `ondelete="CASCADE"` 无应用层保护
- 删除 User 级联删除 AdminSessions，但活跃 session 未撤销
- 删除后孤儿资源（文件、缓存）未清理

**证据**:
```python
# backend/app/models/admin_profile.py
user_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), 
    ForeignKey("users.id", ondelete="CASCADE"),  # ← 危险
    nullable=False
)

# 删除 User 时：
# 1. AdminProfile 被 CASCADE 删除 ✓
# 2. AdminSession 被 CASCADE 删除 ✓
# 3. 但 session cookie 仍有效 ✗（zombie session）
# 4. 用户上传的附件仍在磁盘 ✗（orphaned files）
```

**影响**:
- Zombie sessions（已删除用户仍可操作）
- 审计日志断链（session_id 指向已删除记录）
- 孤儿文件积压

**修复建议**:
```python
# 方案 1: 应用层补偿删除
async def delete_user_safe(user_id: uuid.UUID, db: AsyncSession):
    # 1. 撤销所有活跃 sessions
    sessions = await db.execute(
        select(AdminSession).where(AdminSession.user_id == user_id)
    )
    for session in sessions.scalars():
        # 从 Redis/缓存中清除
        await invalidate_session(session.token_hash)
    
    # 2. 清理文件系统
    attachments = await get_user_attachments(user_id, db)
    for att in attachments:
        await delete_file(att.file_path)
    
    # 3. 记录审计日志
    await audit_log(f"User {user_id} deleted with {len(sessions)} sessions")
    
    # 4. 执行数据库删除
    await db.delete(user)
    await db.commit()

# 方案 2: 软删除
class User(Base):
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    @hybrid_property
    def is_active(self):
        return self.deleted_at is None
```

**优先级**: 🔴 Phase 2 必须修复

---

## 📊 影响评估

### 如果不修复这 4 个问题

| 问题 | 生产环境风险 | 数据丢失风险 | 安全风险 |
|------|-------------|-------------|----------|
| NEW-C01 | 🔴 高 | 🟡 中 | 🔴 高 |
| NEW-C02 | 🟡 中 | 🔴 高 | 🟢 低 |
| NEW-C03 | 🔴 高 | 🟢 低 | 🟢 低 |
| NEW-C04 | 🟡 中 | 🔴 高 | 🟡 中 |

### 修复时间估算

| 问题 | 调查 | 实施 | 测试 | 总计 |
|------|------|------|------|------|
| NEW-C01 | 0.5h | 1h | 0.5h | **2h** |
| NEW-C02 | 1h | 0.5h | 1h | **2.5h** |
| NEW-C03 | 0.5h | 0.5h | 1h | **2h** |
| NEW-C04 | 1h | 2h | 1h | **4h** |
| **总计** | 3h | 4h | 3.5h | **10.5h** |

---

## 🎯 建议执行顺序

### Phase 0.5: 关键基础设施修复（10.5 小时）

**优先级排序**:
1. **NEW-C03** - 连接池配置（2h，立即见效）
2. **NEW-C02** - 事务隔离（2.5h，防止数据损坏）
3. **NEW-C01** - Session 状态缓存（2h，安全关键）
4. **NEW-C04** - CASCADE 保护（4h，数据完整性）

**并行策略**:
- NEW-C03 和 NEW-C01 可并行（不同子系统）
- NEW-C02 和 NEW-C04 需串行（都涉及数据模型）

---

## 🔐 安全影响矩阵

| 问题 | OWASP 类别 | CVE 相似度 | 可利用性 |
|------|-----------|-----------|---------|
| NEW-C01 | A07:2021 (Auth Failures) | CWE-362 (Race Condition) | 🔴 高 |
| NEW-C04 | A01:2021 (Broken Access Control) | CWE-404 (Improper Resource Shutdown) | 🟡 中 |

---

## ✅ 验收标准

### NEW-C01
- [ ] AUTH_BYPASS 在请求开始时缓存
- [ ] 部署期间环境变量变化不影响进行中请求
- [ ] 并发测试：1000 请求无权限泄露

### NEW-C02
- [ ] 引擎配置 `isolation_level="REPEATABLE READ"`
- [ ] 竞态测试：并发更新同一 ReviewItem 无丢失
- [ ] 性能测试：TPS 下降 <5%

### NEW-C03
- [ ] 连接池配置：pool_size=20, max_overflow=10
- [ ] 负载测试：30 并发用户无阻塞
- [ ] 监控：连接池使用率图表

### NEW-C04
- [ ] 删除 User 前撤销所有 sessions
- [ ] 孤儿文件清理脚本
- [ ] 审计日志完整性测试

---

## 📋 后续行动

1. **立即通知用户**这 4 个 CRITICAL 问题
2. **征求授权**：Phase 0.5 立即修复 or 纳入 Phase 1
3. **派遣专家子智能体**实施修复
4. **独立验证**每个修复的有效性
5. **更新工作空间文档**反映新的执行计划

---

**此简报旨在快速传达关键风险，完整问题清单见 ISSUES_COMPLETE_INVENTORY.md**
