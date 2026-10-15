# 数据库环境管理补充

## 当前状态分析 ⚠️

### 已有的安全机制 ✅

**scratch_db_safety.py** 提供了基本保护：
- 测试必须使用 `astra_week3_*` 或 `astra_week4_*` 命名的本地数据库
- 拒绝连接生产数据库（`blog_v2`, `blog_db`）
- 仅允许 localhost/127.0.0.1 连接

### 存在的问题 ❌

1. **没有统一的环境配置管理**
   - `.env` / `.env.development` / `.env.production` 混乱
   - `DATABASE_URL` 在不同环境可能指向同一个库
   - 没有明确的环境隔离策略

2. **测试数据库命名不统一**
   - 有 `astra_week3_*`, `astra_week4_*` 但没有统一规则
   - 没有自动创建/清理机制
   - 没有隔离不同测试套件

3. **生产数据库保护不足**
   - 仅依赖命名检查（可以绕过）
   - 没有显式的生产环境标记
   - 没有迁移执行的双重确认

---

## 补充需求：统一数据库环境管理

### REQ-ENV-001: 明确的环境分层 [P0]

**目标**：建立清晰的数据库环境边界

```yaml
environments:
  development:
    database: blog_dev
    purpose: 本地开发
    data: 可随意修改
    location: localhost
  
  test:
    database: astra_test_{suite_name}
    purpose: 自动化测试
    data: 每次测试前重建
    location: localhost
    
  staging:
    database: blog_staging
    purpose: 预发布验证
    data: 接近生产的测试数据
    location: 独立服务器
    
  production:
    database: blog_production
    purpose: 生产环境
    data: 真实用户数据
    location: 生产服务器
    protection: 双重确认 + 审计
```

**验收标准**：
- AC-ENV-001-1: 每个环境有独立的 DATABASE_URL
- AC-ENV-001-2: ENV 变量明确标识环境
- AC-ENV-001-3: 配置文件按环境分离（.env.development, .env.test, .env.production）
- AC-ENV-001-4: 生产环境配置不入 Git

---

### REQ-ENV-002: 测试数据库自动化管理 [P1]

**目标**：统一测试数据库的创建、使用和清理

**命名规则**：
```python
TEST_DB_PATTERN = "blog_test_{purpose}_{timestamp}"

# 示例
blog_test_unit_20261013_143022        # 单元测试
blog_test_integration_20261013_143100 # 集成测试
blog_test_e2e_20261013_143200         # E2E 测试
blog_test_manual_john_20261013        # 手动测试
```

**自动化脚本**：
```python
# backend/tests/db_manager.py
import asyncio
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

class TestDatabaseManager:
    """测试数据库管理器"""
    
    @staticmethod
    async def create_test_db(purpose: str = "test") -> str:
        """创建隔离的测试数据库"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_name = f"blog_test_{purpose}_{timestamp}"
        
        # 连接到 postgres 系统库创建测试库
        admin_url = "postgresql+asyncpg://user:password@localhost/postgres"
        engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
        
        async with engine.connect() as conn:
            await conn.execute(text(f"CREATE DATABASE {db_name}"))
        
        await engine.dispose()
        
        test_url = f"postgresql+asyncpg://user:password@localhost/{db_name}"
        return test_url
    
    @staticmethod
    async def drop_test_db(db_url: str):
        """清理测试数据库"""
        from sqlalchemy.engine import make_url
        url = make_url(db_url)
        db_name = url.database
        
        # 安全检查
        if not db_name.startswith("blog_test_"):
            raise ValueError(f"拒绝删除非测试数据库: {db_name}")
        
        admin_url = f"postgresql+asyncpg://{url.username}:{url.password}@{url.host}/postgres"
        engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
        
        async with engine.connect() as conn:
            # 强制断开所有连接
            await conn.execute(text(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{db_name}' AND pid <> pg_backend_pid()
            """))
            await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        
        await engine.dispose()
    
    @staticmethod
    async def cleanup_old_test_dbs(older_than_hours: int = 24):
        """清理旧的测试数据库"""
        admin_url = "postgresql+asyncpg://user:password@localhost/postgres"
        engine = create_async_engine(admin_url)
        
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT datname FROM pg_database
                WHERE datname LIKE 'blog_test_%'
            """))
            test_dbs = [row[0] for row in result]
        
        # 根据时间戳判断是否清理
        # （解析 db_name 中的时间戳）
        for db_name in test_dbs:
            # 实现时间判断逻辑
            pass
        
        await engine.dispose()
```

**Pytest Fixture**：
```python
# backend/tests/conftest.py
import pytest
from tests.db_manager import TestDatabaseManager

@pytest.fixture(scope="session")
async def test_database():
    """Session级别的测试数据库"""
    db_url = await TestDatabaseManager.create_test_db("session")
    
    # 运行迁移
    await run_migrations(db_url)
    
    yield db_url
    
    # 清理
    await TestDatabaseManager.drop_test_db(db_url)

@pytest.fixture(scope="function")
async def isolated_db():
    """Function级别的隔离数据库"""
    db_url = await TestDatabaseManager.create_test_db("function")
    await run_migrations(db_url)
    
    yield db_url
    
    await TestDatabaseManager.drop_test_db(db_url)
```

**验收标准**：
- AC-ENV-002-1: 测试自动创建独立数据库
- AC-ENV-002-2: 测试结束后自动清理
- AC-ENV-002-3: 并发测试使用不同数据库
- AC-ENV-002-4: 手动清理脚本可用

---

### REQ-ENV-003: 生产数据库双重保护 [P0]

**目标**：防止意外操作生产数据库

**保护层级**：

**Layer 1: 环境检测**
```python
# backend/app/config.py
class Settings(BaseSettings):
    ENV: str = "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENV == "production"
    
    @property
    def database_safe_name(self) -> str:
        """安全的数据库名称（隐藏敏感信息）"""
        from sqlalchemy.engine import make_url
        url = make_url(self.DATABASE_URL)
        return f"{url.host}/{url.database}"
```

**Layer 2: 迁移保护**
```python
# backend/alembic/env.py
from app.config import get_settings
from app.utils.scratch_db_safety import require_migration_target

def run_migrations_online():
    settings = get_settings()
    
    # 生产环境需要显式确认
    if settings.is_production:
        approved_target = os.environ.get("BLOG_APPROVED_MIGRATION_TARGET")
        require_migration_target(settings.DATABASE_URL, approved_target=approved_target)
        
        # 要求用户手动确认
        print(f"⚠️  生产数据库迁移: {settings.database_safe_name}")
        print("请输入 'YES' 确认执行:")
        confirmation = input().strip()
        
        if confirmation != "YES":
            raise RuntimeError("生产迁移已取消")
    
    # ... 执行迁移
```

**Layer 3: 操作审计**
```python
# backend/app/middleware/audit.py
class ProductionAuditMiddleware:
    """生产环境审计中间件"""
    
    async def __call__(self, request, call_next):
        if settings.is_production:
            # 记录所有写操作
            if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
                await log_production_write(
                    method=request.method,
                    path=request.url.path,
                    user=await get_current_user(request),
                    timestamp=datetime.now()
                )
        
        return await call_next(request)
```

**验收标准**：
- AC-ENV-003-1: 生产环境迁移需要双重确认
- AC-ENV-003-2: 生产写操作全部审计
- AC-ENV-003-3: 环境变量错误时启动失败（fail-safe）
- AC-ENV-003-4: 测试无法连接生产数据库

---

### REQ-ENV-004: 配置文件标准化 [P1]

**目标**：统一环境配置格式

**文件结构**：
```
backend/
├── .env.example           # 模板（入 Git）
├── .env.development       # 开发配置（入 Git，无密钥）
├── .env.test             # 测试配置（入 Git，无密钥）
├── .env                  # 本地开发（不入 Git）
├── .env.production       # 生产配置（不入 Git，仅部署时创建）
└── config/
    ├── development.py    # 开发默认值
    ├── test.py          # 测试默认值
    └── production.py    # 生产默认值
```

**.env.development**:
```bash
ENV=development
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/blog_dev
AI_API_KEY=sk-dev-key-use-real-key-locally
AUTH_BYPASS=false
AUTH_BYPASS_ALLOW=false  # 开发环境也禁用 bypass
```

**.env.test**:
```bash
ENV=test
# 测试数据库由 TestDatabaseManager 动态创建
# DATABASE_URL 将被 pytest fixture 覆盖
AI_API_KEY=sk-test-fake-key
OCR_AUTO_RECOGNITION_ENABLED=false
AUTH_BYPASS=false
AUTH_BYPASS_ALLOW=false
```

**.env.production** (不入 Git):
```bash
ENV=production
DATABASE_URL=postgresql+asyncpg://prod_user:SECURE_PASSWORD@prod-db.example.com:5432/blog_production
AI_API_KEY=sk-prod-real-key
AUTH_BYPASS=false
AUTH_BYPASS_ALLOW=false  # 生产环境永久禁用
```

**配置加载逻辑**：
```python
# backend/app/config.py
import os
from pathlib import Path

def get_env_file() -> str:
    """根据 ENV 变量选择配置文件"""
    env = os.getenv("ENV", "development")
    
    # 优先级：.env > .env.{ENV}
    if Path(".env").exists():
        return ".env"
    
    env_file = f".env.{env}"
    if Path(env_file).exists():
        return env_file
    
    return ".env.example"

class Settings(BaseSettings):
    model_config = {
        "env_file": get_env_file(),
        "env_file_encoding": "utf-8"
    }
```

**验收标准**：
- AC-ENV-004-1: 所有环境有对应配置文件
- AC-ENV-004-2: .env.production 不入 Git
- AC-ENV-004-3: 配置加载优先级正确
- AC-ENV-004-4: 文档说明配置使用方法

---

## 集成到工作空间

### 在 Phase 1 增加环境验证

**新增任务 T1-ENV**：
```yaml
task: T1-ENV-环境配置验证
依赖: T0 (基线)
执行者: Backend Expert (Haiku)
模式: 只读调查

目标:
1. 审查当前所有 .env* 文件
2. 识别环境混淆风险
3. 验证测试数据库安全机制
4. 生成环境配置报告

产出:
- evidence/p1-baseline/env-audit-report.yaml
- 环境配置问题清单
- 统一化建议
```

### 在 Phase 2 实施统一化

**新增需求 REQ-P2-006**：
```yaml
需求: 统一测试/生产数据库管理
优先级: P1
依赖: T1-ENV 报告

实施内容:
1. 创建 TestDatabaseManager
2. 更新 pytest fixtures
3. 标准化 .env 文件
4. 增强生产保护

验收标准:
- AC-P2-006-1: 测试自动创建/清理数据库
- AC-P2-006-2: 生产迁移需要双重确认
- AC-P2-006-3: 环境配置文档完整
- AC-P2-006-4: CI/CD 使用正确环境
```

### 在 Phase 5 增加环境隔离验证

**后端独立验证增加检查项**：
```yaml
environment_isolation:
  test_db_creation: PASS/FAIL
  test_db_cleanup: PASS/FAIL
  production_protection: PASS/FAIL
  config_file_security: PASS/FAIL
  evidence:
    - evidence/p5-integration/env-isolation-test.txt
```

---

## 快速修复建议（可立即执行）

如果你希望在开始 Phase 1 之前快速修复环境问题，我可以：

1. **创建标准化配置文件**
   - 生成 .env.development, .env.test
   - 更新 .env.example
   - 添加 .gitignore 规则

2. **实现 TestDatabaseManager**
   - 自动创建/清理测试库
   - Pytest fixture 集成

3. **增强生产保护**
   - 迁移双重确认
   - 环境检测

你希望：
- [ ] 现在立即修复环境配置（作为 Phase 0.5）
- [ ] 纳入 Phase 1-2 逐步修复
- [ ] 先了解更多细节再决定

---

## 总结

**当前状态**: 🟡 部分保护，存在风险
- ✅ 有基本的测试数据库保护
- ❌ 没有统一的环境管理
- ❌ 没有自动化测试数据库创建/清理
- ❌ 生产保护不足（仅命名检查）

**建议优先级**: **P1（Phase 1 必须修复）**

环境混淆会导致：
- 测试污染开发数据
- 开发误操作生产数据
- 并发测试互相干扰
- 迁移执行到错误数据库

---

这份补充是否回答了你的问题？需要我：
1. 立即实施快速修复？
2. 详细设计某个部分？
3. 调整优先级？
