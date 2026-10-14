# 系统收敛验证策略

## 验证原则

### 1. 分层独立验证

```
Layer 1: 单元/组件级（Mock 外部依赖）
   ↓
Layer 2: 模块级（真实数据库/API）
   ↓
Layer 3: 集成级（前后端联合）
   ↓
Layer 4: 端到端（真实浏览器 + 完整系统）
```

每层必须独立通过才能进入下一层。

### 2. 证据完整性要求

**每个验收标准（AC-xxx）必须有**：
- 验证命令（可重现）
- 执行输出（完整日志）
- 预期结果 vs 实际结果
- 执行者 agent_id
- 时间戳

**证据文件命名规范**：
```
evidence/
├── p1-baseline/
│   ├── AC-P1-001-1-snapshot-verification.txt
│   ├── AC-P1-002-1-typecheck-output.txt
│   └── ...
├── p2-contracts/
│   ├── AC-P2-001-1-kp-consistency.json
│   ├── AC-P2-002-1-ai-input-test.txt
│   └── ...
├── p3-experience/
│   ├── AC-P3-003-1-flow1-recording.mp4
│   ├── AC-P3-004-2-screenshots/
│   └── ...
└── p5-integration/
    ├── backend-verification-report.yaml
    ├── frontend-verification-report.yaml
    └── integration-report.yaml
```

### 3. 独立性验证

**后端验证不依赖前端**：
- 使用 curl/httpie/pytest 直接测试 API
- 使用 psql 直接查询数据库
- 使用 Python 脚本测试服务层

**前端验证不依赖真实后端**：
- 使用 MSW (Mock Service Worker) 模拟 API
- 使用 Storybook 隔离组件
- 使用 Playwright 测试 UI 交互

**集成验证联合两者**：
- 真实 FastAPI + 真实 Next.js
- 真实 PostgreSQL 数据库
- 真实浏览器环境

---

## Phase 1 验证：基线与类型门禁

### V-P1-001: 基线快照验证

**执行者**: Independent Verifier (Haiku)

**步骤**：
```bash
# 1. 验证快照完整性
cd /Users/limengyang/2025-blog-public
tar -tzf baseline-snapshot.tar.gz | wc -l
# 期望：254 个文件

# 2. 验证 SHA256
sha256sum -c baseline.sha256
# 期望：OK

# 3. 测试恢复
mkdir /tmp/baseline-restore-test
tar -xzf baseline-snapshot.tar.gz -C /tmp/baseline-restore-test

# 4. 对比文件
find /tmp/baseline-restore-test -type f -exec sha256sum {} \; | sort > /tmp/restored.sha256
find . -path ./baseline-snapshot.tar.gz -prune -o -type f -exec sha256sum {} \; | sort > /tmp/original.sha256
diff /tmp/restored.sha256 /tmp/original.sha256
# 期望：无差异

# 5. 清理
rm -rf /tmp/baseline-restore-test
```

**成功标准**：
- 所有命令退出码 0
- 文件数量一致
- SHA256 校验通过
- diff 无输出

---

### V-P1-002: 类型门禁验证

**执行者**: Independent Verifier (Haiku)

**步骤**：
```bash
cd /Users/limengyang/2025-blog-public

# 1. 应用 TS 类型检查
npm run test:typecheck 2>&1 | tee evidence/p1-baseline/typecheck-full.txt
echo "Exit code: $?" >> evidence/p1-baseline/typecheck-full.txt

# 2. 检查特定错误
grep "TS2322" evidence/p1-baseline/typecheck-full.txt | wc -l
# 期望：0

# 3. 检查错误总数
grep -c "error TS" evidence/p1-baseline/typecheck-full.txt || echo "0"
# 期望：0

# 4. 单文件测试
npm test src/app/manage/\(workspace\)/review/review-queue.test.tsx 2>&1 | \
  tee evidence/p1-baseline/review-queue-test.txt

# 5. 完整测试套件
npm test 2>&1 | tee evidence/p1-baseline/full-test-suite.txt

# 6. 提取统计
grep "Tests.*passed" evidence/p1-baseline/full-test-suite.txt
# 期望：≥530 passed
```

**成功标准**：
- typecheck 退出码 0
- 0 个 TS2322 错误
- 受影响测试通过
- ≥530 tests passed

---

### V-P1-003: Schema 门禁验证

**执行者**: Backend Expert (Haiku)

**步骤**：
```bash
cd /Users/limengyang/2025-blog-public/backend

# 1. Alembic 检查
alembic check 2>&1 | tee ../evidence/p1-baseline/alembic-check.txt
echo "Exit code: $?" >> ../evidence/p1-baseline/alembic-check.txt

# 2. Schema Catalog 门禁
PYTHONPATH=. python app/cli.py check-schema-catalog 2>&1 | \
  tee ../evidence/p1-baseline/catalog-gate.txt
echo "Exit code: $?" >> ../evidence/p1-baseline/catalog-gate.txt

# 3. 验证迁移图
alembic history --verbose | tee ../evidence/p1-baseline/migration-history.txt

# 4. 检查 head
alembic current 2>&1 | tee ../evidence/p1-baseline/current-revision.txt
```

**成功标准**：
- alembic check 退出码 0
- catalog gate 退出码 0
- migration graph 完整（无断链）
- current revision 与预期一致

---

## Phase 2 验证：数据合同收敛

### V-P2-001: KP 关系一致性验证

**执行者**: Backend Expert (Haiku)

**测试矩阵**：

| 测试场景 | 操作 | 验证点 | 期望结果 |
|---------|------|--------|---------|
| PUT 替换 KP | PUT /api/admin/questions/{id} | QuestionKnowledgePoint 表 | 新 KP 集合 |
| PATCH 替换 KP | PATCH /api/admin/questions/{id} | 同上 | 新 KP 集合 |
| 读取详情 | GET /api/admin/questions/{id} | knowledge_points 字段 | 与数据库一致 |
| Analytics 查询 | GET /api/admin/knowledge-points/{id}/stats | 题目计数 | 正确关联 |
| Practice 选题 | GET /api/admin/practice/today | 题目 KP | 正确关联 |

**测试脚本**：
```python
# evidence/p2-contracts/test_kp_consistency.py
import pytest
import requests
import psycopg2

def test_kp_put_patch_consistency():
    """测试 PUT 和 PATCH 使用相同写协议"""
    base_url = "http://localhost:8000"
    
    # 1. 创建测试题目
    response = requests.post(f"{base_url}/api/admin/questions", json={
        "stem_md": "Test Question",
        "question_type": "single_choice",
        "options": [{"key": "A", "text": "Option A"}],
        "correct_answer": "A"
    })
    question_id = response.json()["id"]
    
    # 2. PUT 设置 KP
    response = requests.put(f"{base_url}/api/admin/questions/{question_id}", json={
        "knowledge_point_ids": ["kp-1", "kp-2"]
    })
    assert response.status_code == 200
    
    # 3. 新事务查询数据库
    conn = psycopg2.connect("postgresql://localhost/test_db")
    cur = conn.cursor()
    cur.execute("""
        SELECT knowledge_point_id 
        FROM question_knowledge_points 
        WHERE question_id = %s
        ORDER BY knowledge_point_id
    """, (question_id,))
    kps_after_put = [row[0] for row in cur.fetchall()]
    assert kps_after_put == ["kp-1", "kp-2"]
    
    # 4. PATCH 修改 KP
    response = requests.patch(f"{base_url}/api/admin/questions/{question_id}", json={
        "knowledge_point_ids": ["kp-2", "kp-3"]
    })
    assert response.status_code == 200
    
    # 5. 再次查询数据库
    cur.execute("""
        SELECT knowledge_point_id 
        FROM question_knowledge_points 
        WHERE question_id = %s
        ORDER BY knowledge_point_id
    """, (question_id,))
    kps_after_patch = [row[0] for row in cur.fetchall()]
    assert kps_after_patch == ["kp-2", "kp-3"]
    
    # 6. 验证 API 返回一致
    response = requests.get(f"{base_url}/api/admin/questions/{question_id}")
    api_kps = sorted([kp["id"] for kp in response.json()["knowledge_points"]])
    assert api_kps == ["kp-2", "kp-3"]
    
    # 7. 验证 Practice 使用相同数据
    response = requests.get(f"{base_url}/api/admin/practice/today")
    practice_question = next((q for q in response.json() if q["id"] == question_id), None)
    if practice_question:  # 如果被选中
        assert sorted(practice_question["knowledge_point_ids"]) == ["kp-2", "kp-3"]
    
    conn.close()

# 运行测试
pytest evidence/p2-contracts/test_kp_consistency.py -v --tb=short
```

**成功标准**：
- 所有测试 PASS
- 数据库查询与 API 一致
- Practice 查询与数据库一致

---

### V-P2-002: AI 输入来源校验验证

**执行者**: Backend Expert (Haiku)

**测试脚本**：
```python
# evidence/p2-contracts/test_ai_input_validation.py
def test_ai_input_hash_mismatch():
    """测试输入变更时拒绝确认"""
    
    # 1. 生成候选
    response = requests.post("/api/admin/ai/generate-mistake", json={
        "question_id": "q-1",
        "user_answer": "A",
        "user_reasoning": "Initial reasoning"
    })
    run_id = response.json()["run_id"]
    candidate = response.json()["candidate"]
    
    # 2. 修改输入（模拟用户改答案）
    response = requests.patch("/api/admin/mistake-drafts/{draft_id}", json={
        "user_answer": "B"  # 改变答案
    })
    assert response.status_code == 200
    
    # 3. 尝试确认旧候选（输入已变）
    response = requests.post(f"/api/admin/ai/runs/{run_id}/confirm")
    
    # 4. 验证拒绝
    assert response.status_code == 409
    error = response.json()
    assert "input_changed" in error["detail"] or "input" in error["detail"].lower()
    
    # 5. 验证数据库无副作用
    run = requests.get(f"/api/admin/ai/runs/{run_id}").json()
    assert run["status"] != "confirmed"
    assert run["target_id"] is None

def test_ai_input_hash_match():
    """测试输入未变时成功确认"""
    
    # 1. 生成候选
    response = requests.post("/api/admin/ai/generate-mistake", json={
        "question_id": "q-2",
        "user_answer": "A",
        "user_reasoning": "Test reasoning"
    })
    run_id = response.json()["run_id"]
    
    # 2. 不修改输入，直接确认
    response = requests.post(f"/api/admin/ai/runs/{run_id}/confirm")
    
    # 3. 验证成功
    assert response.status_code == 200
    result = response.json()
    assert result["run"]["status"] == "confirmed"
    assert result["run"]["target_id"] is not None
    
    # 4. 验证数据库
    draft = requests.get(f"/api/admin/mistake-drafts/{result['run']['target_id']}").json()
    assert draft["ai_run_id"] == run_id
```

**成功标准**：
- 输入变更时返回 409
- 输入未变时成功确认
- 数据库状态一致

---

### V-P2-003: AI 确认快照验证

**执行者**: Backend Expert (Haiku)

**验证点**：
- confirmed_snapshot 字段存在
- 包含完整候选内容
- 用户编辑正确标记
- 审计可追溯

```python
def test_ai_confirmation_snapshot():
    # 1. 生成候选
    response = requests.post("/api/admin/ai/generate-mistake", json={
        "question_id": "q-3",
        "user_answer": "A"
    })
    run_id = response.json()["run_id"]
    original_candidate = response.json()["candidate"]["analysis"]
    
    # 2. 用户编辑候选
    edited_text = "User edited analysis"
    response = requests.patch(f"/api/admin/ai/runs/{run_id}/candidate", json={
        "analysis": edited_text
    })
    
    # 3. 确认
    response = requests.post(f"/api/admin/ai/runs/{run_id}/confirm")
    assert response.status_code == 200
    
    # 4. 验证快照
    run = requests.get(f"/api/admin/ai/runs/{run_id}").json()
    assert run["confirmed_snapshot"] is not None
    assert run["confirmed_snapshot"]["analysis"] == edited_text
    assert run["edited"] == True  # 标记用户修改
    
    # 5. 验证审计可查
    drafts = requests.get("/api/admin/mistake-drafts").json()
    draft = next(d for d in drafts if d["ai_run_id"] == run_id)
    assert draft["analysis"] == edited_text  # 采纳了确认时的版本
```

---

### V-P2-004: AI 并发确认验证

**执行者**: Backend Expert (Haiku)

**并发测试**：
```python
import asyncio
import aiohttp

async def confirm_async(session, run_id):
    """异步确认请求"""
    async with session.post(
        f"http://localhost:8000/api/admin/ai/runs/{run_id}/confirm"
    ) as resp:
        return resp.status, await resp.json()

async def test_concurrent_confirmation():
    """测试双会话并发确认"""
    
    # 1. 创建候选
    async with aiohttp.ClientSession() as session:
        async with session.post("/api/admin/ai/generate-mistake", json={
            "question_id": "q-4",
            "user_answer": "A"
        }) as resp:
            run_id = (await resp.json())["run_id"]
    
    # 2. 两个会话同时确认
    async with aiohttp.ClientSession() as session_a, \
               aiohttp.ClientSession() as session_b:
        results = await asyncio.gather(
            confirm_async(session_a, run_id),
            confirm_async(session_b, run_id),
            return_exceptions=True
        )
    
    # 3. 验证仅一个成功
    statuses = [r[0] for r in results if not isinstance(r, Exception)]
    success_count = sum(1 for s in statuses if s == 200)
    conflict_count = sum(1 for s in statuses if s == 409)
    
    assert success_count == 1, f"期望 1 个成功，实际 {success_count}"
    assert conflict_count == 1, f"期望 1 个冲突，实际 {conflict_count}"
    
    # 4. 验证数据库一致性
    async with aiohttp.ClientSession() as session:
        async with session.get(f"/api/admin/ai/runs/{run_id}") as resp:
            run = await resp.json()
            assert run["status"] == "confirmed"
            assert run["target_id"] is not None
            
        # 5. 验证仅创建一个 Draft
        async with session.get("/api/admin/mistake-drafts") as resp:
            drafts = await resp.json()
            related_drafts = [d for d in drafts if d.get("ai_run_id") == run_id]
            assert len(related_drafts) == 1

# 运行
asyncio.run(test_concurrent_confirmation())
```

**成功标准**：
- 1 个确认成功（200）
- 1 个确认冲突（409）
- 数据库仅 1 条记录

---

## Phase 3 验证：前端体验

### V-P3-001: Capture 状态隔离验证

**执行者**: Frontend Expert (Haiku)

**Playwright 测试**：
```typescript
// evidence/p3-experience/capture-isolation.spec.ts
import { test, expect } from '@playwright/test';

test('capture switching ignores stale details', async ({ page }) => {
  await page.goto('http://localhost:3000/manage/capture');
  
  // 1. 选择 Capture A
  await page.click('[data-testid="capture-a"]');
  await expect(page.locator('[data-testid="capture-id"]')).toHaveText('capture-a');
  
  // 2. 立即切换到 B（A 的详情可能还在加载）
  await page.click('[data-testid="capture-b"]');
  
  // 3. 等待加载完成
  await page.waitForLoadState('networkidle');
  
  // 4. 验证显示的是 B 的内容
  await expect(page.locator('[data-testid="capture-id"]')).toHaveText('capture-b');
  await expect(page.locator('[data-testid="capture-title"]')).toContainText('Capture B');
  
  // 5. 快速切换 5 次
  for (let i = 0; i < 5; i++) {
    await page.click('[data-testid="capture-a"]');
    await page.click('[data-testid="capture-b"]');
  }
  
  // 6. 最终应显示 B
  await page.waitForLoadState('networkidle');
  await expect(page.locator('[data-testid="capture-id"]')).toHaveText('capture-b');
});

test('capture form resets on switch', async ({ page }) => {
  await page.goto('http://localhost:3000/manage/capture');
  
  // 1. 在 A 中填写表单
  await page.click('[data-testid="capture-a"]');
  await page.fill('[data-testid="user-answer"]', 'Answer for A');
  
  // 2. 切换到 B
  await page.click('[data-testid="capture-b"]');
  
  // 3. 验证表单已清空或显示 B 的数据
  const answer = await page.inputValue('[data-testid="user-answer"]');
  expect(answer).not.toBe('Answer for A');
});
```

**运行**：
```bash
npx playwright test evidence/p3-experience/capture-isolation.spec.ts --headed
```

---

### V-P3-002: Notes 分页验证

**执行者**: Frontend Expert + Backend Expert (联合)

**后端验证**：
```bash
# 1. 创建 25 条笔记
for i in {1..25}; do
  curl -X POST http://localhost:8000/api/notes \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Note $i\", \"note_type\": \"note\", \"content\": \"Content $i\"}"
done

# 2. 验证分页
curl "http://localhost:8000/api/notes?type=note&page=1&per_page=20" | \
  jq 'length' | tee evidence/p3-experience/notes-page1-count.txt
# 期望：20

curl "http://localhost:8000/api/notes?type=note&page=2&per_page=20" | \
  jq 'length' | tee evidence/p3-experience/notes-page2-count.txt
# 期望：5
```

**前端验证**：
```typescript
test('notes pagination loads next page', async ({ page }) => {
  await page.goto('http://localhost:3000/manage/notes');
  
  // 1. 验证第一页
  const firstPageNotes = await page.locator('[data-testid="note-item"]').count();
  expect(firstPageNotes).toBe(20);
  
  // 2. 点击"加载更多"或滚动触发分页
  await page.click('[data-testid="load-more"]');
  
  // 3. 验证第二页加载
  await page.waitForLoadState('networkidle');
  const totalNotes = await page.locator('[data-testid="note-item"]').count();
  expect(totalNotes).toBe(25);
});
```

---

### V-P3-003: 三条流程录屏验证

**执行者**: Independent Verifier (Haiku)

**流程 1: Dashboard → Review → 再答**
```typescript
test('flow 1: dashboard to review with reanswer', async ({ page }) => {
  // 录屏
  await page.video();
  
  await page.goto('http://localhost:3000/manage/dashboard');
  
  // 1. 点击今日复习
  await page.click('[data-testid="today-review"]');
  
  // 2. 验证进入 Review 页面
  await expect(page).toHaveURL(/\/manage\/review/);
  
  // 3. 点击再答
  await page.click('[data-testid="reanswer-button"]');
  
  // 4. 选择答案
  await page.click('[data-testid="option-a"]');
  await page.click('[data-testid="submit-answer"]');
  
  // 5. 等待评价建议
  await expect(page.locator('[data-testid="recommendation"]')).toBeVisible();
  
  // 6. 提交评分
  await page.click('[data-testid="rating-4"]');
  await page.click('[data-testid="submit-review"]');
  
  // 7. 验证成功
  await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
  
  // 8. 查询数据库验证
  // (通过 API 或直接数据库查询)
});
```

**保存录屏**：
```bash
# Playwright 自动保存到
evidence/p3-experience/videos/flow1-dashboard-review-reanswer.webm
```

**流程 2 & 3 类似实现**

---

### V-P3-004: 八维视觉质量验证

**执行者**: Frontend Expert + UX Designer (Haiku)

**检查清单**：
```yaml
visual_quality_checklist:
  typography:
    - [ ] 四级语义层次清晰
    - [ ] 中文正文 16-18px, 1.65-1.85 行高
    - [ ] 英文与公式基线对齐
    - [ ] 长短标题测试
  
  spacing:
    - [ ] 嵌套容器 padding 一致
    - [ ] 基于固定尺度（8px/16px）
    - [ ] 390/768/1440 节奏稳定
  
  visual_hierarchy:
    - [ ] 主要动作突出
    - [ ] 导航不重复争夺注意
    - [ ] 错误状态显眼
  
  color:
    - [ ] 语义 token 统一
    - [ ] 对比度 ≥4.5:1 (正文)
    - [ ] 对比度 ≥3:1 (大文本)
    - [ ] 状态不只靠颜色区分
  
  animation:
    - [ ] 状态变化有解释
    - [ ] 反馈 120-180ms
    - [ ] 面板 180-260ms
    - [ ] reduced-motion 支持
  
  micro_interactions:
    - [ ] 提交中禁用防重
    - [ ] 失败保留输入
    - [ ] 成功可感知
    - [ ] 焦点有去处
  
  responsive:
    - [ ] 390px 可用
    - [ ] 768px 可用
    - [ ] 1440px 可用
    - [ ] 软键盘不遮挡输入
    - [ ] 触控目标 ≥44px
  
  originality:
    - [ ] 学习手稿编辑感
    - [ ] 个人品牌一致
    - [ ] 不照搬获奖站装饰
```

**截图证据**：
```bash
evidence/p3-experience/screenshots/
├── desktop-1440px/
│   ├── dashboard.png
│   ├── review.png
│   ├── notes.png
│   └── ...
├── tablet-768px/
│   └── ...
├── mobile-390px/
│   └── ...
└── contrast-check/
    ├── text-on-background.png
    └── measurements.json
```

**对比度测量**：
```bash
# 使用工具自动测量
npx @axe-core/cli http://localhost:3000/manage/dashboard \
  --tags wcag2aa,color-contrast \
  --save evidence/p3-experience/contrast-report.json
```

---

## Phase 5: 前后端联合检查

### V-P5-001: 后端独立验证报告

**执行者**: Backend Expert (Haiku) - 独立实例

**验证模板**：
```yaml
backend_verification_report:
  date: 2026-10-XX
  verifier_id: backend-expert-haiku-xyz
  independence_confirmed: true  # 未参与后端实施
  
  schema_consistency:
    alembic_check: PASS
    catalog_gate: PASS
    orm_model_match: PASS
    constraints_verified: PASS
    evidence:
      - evidence/p5-integration/alembic-check.txt
      - evidence/p5-integration/catalog-gate.txt
  
  api_contracts:
    total_endpoints: 197
    tested_endpoints: 197
    passed: 195
    failed: 2
    failed_details:
      - endpoint: POST /api/admin/questions
        issue: "Schema validation allows invalid difficulty"
        severity: MEDIUM
      - endpoint: GET /api/notes
        issue: "Pagination header missing"
        severity: LOW
    evidence:
      - evidence/p5-integration/api-contract-tests.json
  
  business_invariants:
    kp_write_protocol: PASS
    ai_confirmation_atomicity: PASS
    review_scheduling: PASS
    mistake_conversion: PASS
    evidence:
      - evidence/p5-integration/business-invariant-tests.json
  
  data_persistence:
    transaction_rollback: PASS
    new_transaction_read: PASS
    foreign_key_cascade: PASS
    concurrent_update: PASS
    evidence:
      - evidence/p5-integration/persistence-tests.json
  
  blocking_issues:
    - issue_id: B-FAIL-001
      description: "Question difficulty schema mismatch"
      severity: MEDIUM
      impact: "Invalid data can be saved"
      recommendation: "Fix schema validation before release"
  
  overall_status: PARTIAL  # 有 2 个失败项
  recommendation: "修复 B-FAIL-001 和 002 后可进入集成验证"
```

---

### V-P5-002: 前端独立验证报告

**执行者**: Frontend Expert (Haiku) - 独立实例

**验证模板**：
```yaml
frontend_verification_report:
  date: 2026-10-XX
  verifier_id: frontend-expert-haiku-abc
  independence_confirmed: true
  
  component_isolation:
    async_state_handling: PASS
    stale_response_protection: PASS
    entity_switching_cleanup: PASS
    evidence:
      - evidence/p5-integration/component-tests.json
  
  user_interactions:
    flow1_dashboard_review: PASS
    flow2_capture_conversion: PASS
    flow3_notes_editing: PASS
    keyboard_navigation: PASS
    touch_targets: PASS
    evidence:
      - evidence/p5-integration/flow1-recording.webm
      - evidence/p5-integration/flow2-recording.webm
      - evidence/p5-integration/flow3-recording.webm
  
  visual_quality:
    typography: PASS
    spacing: PASS
    visual_hierarchy: PASS
    color_contrast: PARTIAL  # 3 处对比度不足
    animation: PASS
    micro_interactions: PASS
    responsive: PASS
    originality: PASS
    evidence:
      - evidence/p5-integration/screenshots/
      - evidence/p5-integration/contrast-report.json
  
  accessibility:
    aria_labels: PASS
    keyboard_navigation: PASS
    screen_reader: PARTIAL  # 2 处缺失标签
    focus_management: PASS
    evidence:
      - evidence/p5-integration/axe-report.json
      - evidence/p5-integration/screen-reader-test.txt
  
  blocking_issues:
    - issue_id: F-FAIL-001
      description: "Dashboard weak KP 对比度 3.2:1"
      severity: LOW
      impact: "WCAG AA 不达标"
      recommendation: "调整颜色或增加字重"
    
    - issue_id: F-FAIL-002
      description: "Review 评分按钮缺失 aria-label"
      severity: MEDIUM
      impact: "读屏器用户无法理解"
      recommendation: "添加描述性标签"
  
  overall_status: PARTIAL
  recommendation: "修复 F-FAIL-002 后可进入集成验证，F-FAIL-001 可延后"
```

---

### V-P5-003: 集成验证报告

**执行者**: Independent Verifier (Haiku) - 第三方

**验证模板**：
```yaml
integration_verification_report:
  date: 2026-10-XX
  verifier_id: integration-verifier-haiku-def
  independence_confirmed: true
  backend_expert_id: backend-expert-haiku-xyz
  frontend_expert_id: frontend-expert-haiku-abc
  
  e2e_flows:
    flow1_dashboard_review_reanswer:
      browser_test: PASS
      database_verification: PASS
      api_calls_correct: PASS
      evidence:
        - evidence/p5-integration/e2e-flow1.webm
        - evidence/p5-integration/e2e-flow1-db-state.json
    
    flow2_capture_conversion:
      browser_test: PASS
      idempotency_verified: PASS
      evidence:
        - evidence/p5-integration/e2e-flow2.webm
    
    flow3_notes_editing:
      browser_test: PASS
      persistence_verified: PASS
      evidence:
        - evidence/p5-integration/e2e-flow3.webm
  
  race_conditions:
    concurrent_ai_confirmation: PASS
    stale_response_after_switch: PASS
    double_submit_protection: PASS
    evidence:
      - evidence/p5-integration/race-condition-tests.json
  
  error_handling:
    network_failure_retry: PASS
    server_error_display: PASS
    validation_error_feedback: PASS
    evidence:
      - evidence/p5-integration/error-handling-tests.json
  
  dependencies_on_backend: 
    - B-FAIL-001  # Question difficulty
    - B-FAIL-002  # Pagination header
  
  dependencies_on_frontend:
    - F-FAIL-002  # ARIA labels
  
  blocking_issues:
    - issue_id: I-FAIL-001
      description: "Capture 转换后偶尔返回 404"
      severity: HIGH
      impact: "用户操作失败"
      root_cause: "后端竞态条件"
      recommendation: "增加重试逻辑或修复后端"
  
  overall_status: BLOCKED  # 有 HIGH 级阻断
  recommendation: "修复 I-FAIL-001 和前置依赖后重新集成验证"
```

---

## 最终接受报告模板

```yaml
final_acceptance_report:
  date: 2026-10-XX
  primary_owner: opus-5.5-main-agent
  
  phase_completion:
    phase1_baseline: COMPLETE
    phase2_contracts: COMPLETE
    phase3_experience: PARTIAL  # 视觉有改进空间
    phase4_acceptance: COMPLETE
    phase5_integration: PARTIAL  # 有剩余问题
  
  verification_independence:
    backend_implementer: agent-001
    backend_reviewer: agent-002
    backend_verifier: agent-003
    frontend_implementer: agent-004
    frontend_reviewer: agent-005
    frontend_verifier: agent-006
    integration_verifier: agent-007
    all_different: true
    no_self_review: true
  
  p0_requirements:
    total: 15
    complete: 13
    partial: 2
    blocked: 0
    details:
      - REQ-P2-001: COMPLETE  # KP 统一
      - REQ-P2-002: COMPLETE  # AI 输入
      - REQ-P2-003: COMPLETE  # AI 快照
      - REQ-P2-004: PARTIAL   # AI 并发（1 个竞态 bug）
      - ...
  
  p1_requirements:
    total: 8
    complete: 6
    partial: 2
    blocked: 0
  
  system_status_change:
    before: PARTIAL
    after: VERIFIED_BASELINE
    confidence: HIGH
  
  remaining_work:
    - I-FAIL-001: Capture 转换竞态
    - F-FAIL-001: 对比度优化
    - 视觉迭代继续（不阻断发布）
  
  release_readiness: CONDITIONAL
  conditions:
    - "修复 I-FAIL-001 后可发布"
    - "F-FAIL-001 和视觉优化可后续迭代"
  
  evidence_completeness: COMPLETE
  evidence_files_count: 87
  
  final_decision: ACCEPT_WITH_CONDITIONS
  
  next_steps:
    - 修复 I-FAIL-001
    - 重跑集成验证
    - 准备发布 checklist
    - 启动视觉迭代计划
```

---

## 证据归档

所有证据文件永久保存：
```
evidence/
├── manifest.json          # 所有证据的索引
├── p1-baseline/
├── p2-contracts/
├── p3-experience/
├── p5-integration/
└── final-acceptance/
    ├── summary.yaml
    ├── backend-report.yaml
    ├── frontend-report.yaml
    └── integration-report.yaml
```

**manifest.json 示例**：
```json
{
  "baseline_date": "2026-10-13",
  "completion_date": "2026-11-XX",
  "total_files": 87,
  "phases": {
    "p1": {"files": 12, "status": "COMPLETE"},
    "p2": {"files": 28, "status": "COMPLETE"},
    "p3": {"files": 35, "status": "PARTIAL"},
    "p5": {"files": 12, "status": "PARTIAL"}
  },
  "key_evidence": [
    {"file": "p5-integration/backend-report.yaml", "type": "verification_report"},
    {"file": "p5-integration/frontend-report.yaml", "type": "verification_report"},
    {"file": "p5-integration/integration-report.yaml", "type": "verification_report"},
    {"file": "final-acceptance/summary.yaml", "type": "acceptance_report"}
  ]
}
```
