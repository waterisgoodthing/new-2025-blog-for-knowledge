# 实际执行计划

**日期**: 2026-10-13  
**当前状态**: 服务运行中，前端构建PASS，后端测试有数据库配置问题

---

## 现状检查结果

### ✅ 前端
- 服务运行正常（localhost:2025）
- 构建成功，无TypeScript错误
- 页面能加载

### ❌ 后端
- 测试需要 `astra_week3_*` 数据库
- DATABASE_URL 未配置测试库
- 连接池：未检查（需要先修复测试）

### ⚠️ 待确认
- A13 TypeScript类型错误（npx tsc 无输出，可能已修复？）
- 页面加载阻断（首页能加载，/manage 需要验证）

---

## 立即修复任务（15 分钟）

### T1: 连接池配置 [P0]
**状态**: ✅ 已验证缺失  
**根因**: `backend/app/database.py` 无 pool_size 等参数

**修复方案**:
```python
# backend/app/database.py（已修改）
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)
```

**验收标准**:
- [x] 代码已修改（完成）
- [ ] 用户确认提交
- [ ] 服务重启验证

**预计时间**: 5 分钟  
**实际状态**: 🔍 等待用户确认是否提交

---

### T2: 测试环境配置 [P0]
**状态**: ✅ 已验证问题  
**根因**: backend/.env 不存在，测试找不到 DATABASE_URL

**发现**: 已有 25+ 个 `astra_week4_*` 测试库

**修复方案**:
```bash
# 使用已有的 CI 测试库
echo 'DATABASE_URL=postgresql://limengyang@localhost/astra_week4_ci' > backend/.env

# 验证测试能运行
cd backend && PYTHONPATH=. .venv/bin/pytest tests/ -v -x
```

**验收标准**:
- [ ] backend/.env 已创建
- [ ] pytest 能启动（无连接错误）
- [ ] 至少 1 个测试通过

**预计时间**: 10 分钟  
**实际状态**: 📝 待执行（需要用户授权）

---

### T3: 验证 TypeScript 类型错误 [P0]
**问题**: A13 声称有类型错误，但 `npx tsc --noEmit` 无输出

**验证方案**:
```bash
# 1. 检查 tsconfig.json 是否排除了某些文件
cat tsconfig.json | grep exclude

# 2. 检查测试文件
npx tsc --noEmit --project tsconfig.test.json

# 3. 查找具体错误
grep -r "review-queue.test.tsx.*169" src/
```

**如果存在错误**:
```typescript
// 修复类型声明
let release: ((value: ReanswerResult) => void) | undefined
// 改为
let release: ((value: ReanswerResult | PromiseLike<ReanswerResult>) => void) | undefined
```

**验收标准**:
- [ ] `npx tsc --noEmit` 零错误
- [ ] `npm run test:typecheck` 通过
- [ ] CI 构建通过

**预计时间**: 30 分钟（验证 + 修复）

---

### T4: 检查 /manage 页面加载 [P0]
**问题**: DESIGN-004 报告页面"一直加载中"

**验证方案**:
```bash
# 1. 启动服务
npm run dev

# 2. 打开浏览器
open http://localhost:2025/manage

# 3. 检查 Network 面板
# - 是否有 401/403 错误？
# - 是否有请求超时？
# - 是否有 CORS 错误？

# 4. 检查 Console
# - 是否有 JavaScript 错误？
# - 是否有认证失败？
```

**如果确实阻断**:
```typescript
// 可能原因：
// 1. AuthGate 卡住
// 2. API 请求失败
// 3. SWR 配置问题

// 需要根据实际情况修复
```

**验收标准**:
- [ ] /manage 页面正常显示 Dashboard
- [ ] 无"加载中"无限循环
- [ ] 页面加载时间 <2 秒

**预计时间**: 2 小时（调查 + 修复）

---

## 今日时间表

```
09:00-10:00  T1: 测试数据库配置（1h）
10:00-10:30  T2: 连接池验证（0.5h）
10:30-11:00  T3: TypeScript验证（0.5h）
11:00-13:00  T4: 页面加载检查（2h）
13:00-14:00  午休
14:00-16:00  修复发现的问题
16:00-17:00  验证 + 文档更新
```

**总计**: 6-7 小时

---

## 明日及后续（取决于今日结果）

### 如果今日 4 项全部 PASS
→ 系统基本可用，可以开始数据合同修复（A01-A04）

### 如果有 1-2 项 FAIL
→ 继续修复，延后 1-2 天

### 如果有 3+ 项 FAIL
→ 重新评估，可能需要更基础的修复

---

## 验收状态标记规范

**每个任务必须明确标记以下之一**:

- `✅ PASS` - 验收标准全部满足，有证据
- `❌ FAIL` - 验收标准未满足，有具体失败原因
- `⚠️ PARTIAL` - 部分满足，说明哪些满足/哪些不满足
- `⏸️ BLOCKED` - 被其他任务阻断，说明阻断原因
- `🔍 INVESTIGATING` - 正在调查中
- `📝 NOT_STARTED` - 尚未开始

**格式**:
```
### T1: 任务名称 [优先级]

**验收标准**:
- [ ] 标准 1
- [ ] 标准 2
- [ ] 标准 3

**实际结果**: ✅ PASS

**证据**:
- pytest 通过截图: evidence/t1-pytest-pass.png
- 测试输出: evidence/t1-output.txt
- 执行命令: `cd backend && PYTHONPATH=. .venv/bin/pytest tests/ -v`
```

---

## 证据归档

所有验收证据保存到：
```
evidence/
├── 2026-10-13/
│   ├── t1-database-config/
│   │   ├── pytest-output.txt
│   │   ├── database-url.txt
│   │   └── migration-log.txt
│   ├── t2-connection-pool/
│   │   ├── database-py-before.txt
│   │   ├── database-py-after.txt
│   │   └── load-test-result.txt
│   ├── t3-typescript/
│   │   ├── tsc-output.txt
│   │   └── fixed-code.diff
│   └── t4-page-loading/
│       ├── network-inspector.png
│       ├── console-log.txt
│       └── page-screenshot.png
```

---

**下一步**: 开始执行 T1
