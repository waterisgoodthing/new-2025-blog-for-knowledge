# 系统收敛需求定义

基于 [ARCHITECTURE_AUDIT](../../audits/ARCHITECTURE_AUDIT.md) A01-A15 问题和 [DESIGN_RATIONALE_REVIEW](../../architecture/DESIGN_RATIONALE_REVIEW.md) DR-B01-B06 建议制定。

## 总体目标

将系统从 **PARTIAL（部分完成）** 状态推进到 **可验证的运行基线**，具备：
- 数据合同一致性
- 学习链路完整性
- 前后端分离可验证性
- 基本视觉体验达标

## 优先级分级

| 优先级 | 定义 | 必须满足条件 |
|--------|------|-------------|
| P0 | 阻断发布，数据正确性风险 | Phase 4 前必须闭合 |
| P1 | 影响核心流程，用户可感知 | Phase 4 前必须闭合或有明确缓解 |
| P2 | 改善体验，技术债 | 可延后，但需明确计划 |
| P3 | 未来能力 | 不在当前范围 |

---

## Phase 1: 基线保护与类型门禁（N00-N01）

### REQ-P1-001: 可恢复源码基线 [P0]

**来源**: N00, B00

**需求**:
- 当前工作区（131 staged + 123 untracked）建立哈希快照
- 可恢复副本（不是临时哈希控制）
- 验证恢复后文件一致性

**验收标准**:
- AC-P1-001-1: 快照包含所有脏文件（254 个）
- AC-P1-001-2: 恢复命令可执行且通过验证
- AC-P1-001-3: 恢复后 `git diff` 与原工作区一致

**验证方法**:
```bash
# 创建快照
tar -czf baseline-snapshot.tar.gz <所有脏文件>
sha256sum baseline-snapshot.tar.gz > baseline.sha256

# 验证恢复
mkdir /tmp/restore-test
tar -xzf baseline-snapshot.tar.gz -C /tmp/restore-test
diff -r /tmp/restore-test /Users/limengyang/2025-blog-public
```

---

### REQ-P1-002: TypeScript 类型门禁通过 [P0]

**来源**: A13, N01

**需求**:
- 修复 `review-queue.test.tsx:169,219` TS2322 错误
- 保持测试行为不变
- 不引入新的类型错误

**验收标准**:
- AC-P1-002-1: `npm run test:typecheck` 退出码 0
- AC-P1-002-2: 无 TS2322 错误
- AC-P1-002-3: 受影响测试全部 PASS
- AC-P1-002-4: 530 个现有测试不退化

**验证方法**:
```bash
npm run test:typecheck 2>&1 | tee evidence/typecheck.txt
npm test src/app/manage/\(workspace\)/review/review-queue.test.tsx
npm test # 完整测试套件
```

**非需求**:
- 不修改测试框架或 tsconfig 绕过检查
- 不修改业务逻辑代码

---

### REQ-P1-003: Schema 定义门禁前置验证 [P0]

**来源**: B04, N00

**需求**:
- 任何后续 Schema 变更前必须通过 B04 门禁
- ORM 模型与 catalog 定义一致
- 精确 allowlist 与 manifest 验证

**验收标准**:
- AC-P1-003-1: `alembic check` 通过
- AC-P1-003-2: `python backend/app/cli.py check-schema-catalog` 通过
- AC-P1-003-3: CI 双门禁配置正确

**验证方法**:
```bash
cd backend
alembic check
PYTHONPATH=. python app/cli.py check-schema-catalog
```

---

## Phase 2: 数据合同收敛（N02-N03）

### REQ-P2-001: KP 关系统一写协议 [P0]

**来源**: A04, DR-B01, N03

**当前问题**:
- `question_service.py:312-326` PUT 只改 KnowledgePointLink（多态）
- `question_service.py:404-422` PATCH 同时改 QuestionKnowledgePoint（专用）
- 读取和练习优先使用专用关系
- **影响**: 编辑结果与读取/练习依据不一致

**需求**:
- 统一 replace-question-KP 操作
- 建议专用关系为规范来源
- 多态表作为兼容投影（如需保留）
- PUT 和 PATCH 使用相同写协议

**验收标准**:
- AC-P2-001-1: PUT 和 PATCH 同时更新专用关系
- AC-P2-001-2: 读取、analytics、practice 全部使用专用关系
- AC-P2-001-3: 新事务查询验证 KP 一致性
- AC-P2-001-4: API 合同测试覆盖 replace 场景

**验证方法**:
```python
# 测试脚本
def test_kp_replace_consistency():
    # PUT question KP
    response = client.put(f"/api/admin/questions/{qid}", json={
        "knowledge_point_ids": [kp1, kp2]
    })
    assert response.status_code == 200
    
    # 新事务查询
    detail = client.get(f"/api/admin/questions/{qid}")
    assert set(detail["knowledge_points"]) == {kp1, kp2}
    
    # Practice 查询
    practice = client.get("/api/admin/practice/today")
    question = next(q for q in practice if q["id"] == qid)
    assert set(question["knowledge_point_ids"]) == {kp1, kp2}
```

**设计约束**:
- 不授权删除多态表（兼容性未完全确认）
- 不授权直接迁移现有数据
- 保留现有 API 端点

---

### REQ-P2-002: AI 生成输入来源校验 [P0]

**来源**: A01, DR-B02, N02

**当前问题**:
- `admin_mistakes.py:156-169` 生成时计算 input_hash
- 确认时仅核对 Question id/version，不核对输入变化
- 用户修改答案/错因后，迟到响应直接覆盖

**需求**:
- 生成时保存完整输入快照（题目 ID、版本、用户答案、错因）
- 确认时核对输入 hash
- 输入不匹配拒绝确认，提示用户重新生成

**验收标准**:
- AC-P2-002-1: 生成时保存 input_hash 和 input_snapshot
- AC-P2-002-2: 确认时 hash 不匹配返回 409 Conflict
- AC-P2-002-3: 前端显示"输入已变更，请重新生成"
- AC-P2-002-4: 测试覆盖：生成 A → 改答案 → 确认 A（拒绝）

**验证方法**:
```python
def test_ai_confirmation_input_mismatch():
    # 生成候选
    run_id = create_ai_candidate(question_id, user_answer="A")
    
    # 修改输入（模拟用户改答案）
    update_draft(draft_id, user_answer="B")
    
    # 尝试确认旧候选
    response = confirm_candidate(run_id)
    assert response.status_code == 409
    assert "input_changed" in response.json()["detail"]
```

---

### REQ-P2-003: AI 确认最终快照保存 [P0]

**来源**: A02, DR-B02, N02

**当前问题**:
- `admin_mistakes.py:206-235` candidate 只进入 hash
- 确认后没有保存最终快照
- 无法重建人工确认时的准确内容

**需求**:
- 确认时保存 confirmed_snapshot（候选内容 + 用户编辑）
- 区分"参考候选"和"采纳字段"语义
- 支持 edited 标记（用户修改了候选）

**验收标准**:
- AC-P2-003-1: 确认后 MistakeDraft 包含 confirmed_snapshot
- AC-P2-003-2: 候选采纳时，字段值来自 confirmed_snapshot
- AC-P2-003-3: edited 标记正确反映用户是否修改
- AC-P2-003-4: 审计查询可追溯确认时内容

**验证方法**:
```python
def test_ai_confirmation_snapshot():
    # 生成候选
    run_id = create_ai_candidate(question_id, candidate_text="AI 生成错因")
    
    # 用户编辑后确认
    edit_candidate(run_id, text="用户修改后错因")
    response = confirm_candidate(run_id)
    
    # 验证快照
    draft = get_draft(response.json()["draft_id"])
    assert draft["confirmed_snapshot"]["text"] == "用户修改后错因"
    assert draft["edited"] == True
    
    # 新事务查询
    audit = get_ai_run(run_id)
    assert audit["confirmed_snapshot"] is not None
```

---

### REQ-P2-004: AI 确认并发原子协议 [P0]

**来源**: A03, DR-B02, N02

**当前问题**:
- `ai_creation_service.py:106-117` confirm 有行锁
- `ai_run_service.py:277-307` 通用 decision 只有内存 revision 检查
- 两会话并发 confirm/reject 可能冲突

**需求**:
- 统一 confirm/reject/accept 的原子协议
- 共享锁机制或 CAS（Compare-And-Swap）
- 至多一个决定生效，其他返回 409

**验收标准**:
- AC-P2-004-1: 双会话并发 confirm，仅一个成功
- AC-P2-004-2: 失败方返回 409 Conflict，不产生副作用
- AC-P2-004-3: 成功方的 target 状态正确关联
- AC-P2-004-4: 回滚测试：失败方事务完全撤销

**验证方法**:
```python
async def test_concurrent_ai_confirmation():
    run_id = create_ai_candidate(question_id)
    
    # 两个会话同时确认
    results = await asyncio.gather(
        confirm_candidate_async(run_id, session_a),
        confirm_candidate_async(run_id, session_b),
        return_exceptions=True
    )
    
    # 验证仅一个成功
    success = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    assert len(success) == 1
    assert len(failures) == 1
    assert "409" in str(failures[0])
    
    # 验证数据库状态一致
    run = get_ai_run(run_id)
    assert run["status"] == "confirmed"
    assert run["target_id"] is not None
```

---

### REQ-P2-005: 输入合同长度与枚举一致性 [P1]

**来源**: A05, A06, N03

**当前问题**:
- A05: `source_ref` schema 允许 500，ORM/migration 为 64
- A06: Draft schema 接受 `unspecified`，DB CHECK 排除

**需求**:
- 统一 DTO/ORM/DB 的长度限制
- 统一枚举值（允许或都排除 unspecified）
- HTTP 验证早于 DB 错误

**验收标准**:
- AC-P2-005-1: `source_ref` 在所有层面一致（建议 500 或明确截断）
- AC-P2-005-2: Draft difficulty 枚举一致
- AC-P2-005-3: 边界测试：65 字符 source_ref
- AC-P2-005-4: 边界测试：unspecified difficulty

**验证方法**:
```bash
# 65 字符测试
curl -X POST /api/admin/questions \
  -d '{"source_ref": "'$(printf 'a%.0s' {1..65})'"}' \
  -H "Content-Type: application/json"
# 期望：HTTP 400 或接受（取决于设计决策）

# unspecified 测试
curl -X POST /api/admin/question-drafts \
  -d '{"difficulty": "unspecified"}' \
  -H "Content-Type: application/json"
# 期望：一致的接受或拒绝行为
```

---

## Phase 3: 前端体验与交互（N04 + 视觉）

### REQ-P3-001: Capture 状态身份隔离 [P1]

**来源**: A11, N04

**当前问题**:
- `capture-workspace.tsx:279-287` 详情响应无代次标记
- 切换 Capture A→B 后，A 的迟到响应覆盖 B

**需求**:
- 详情响应包含 `capture_id`
- 前端按 `current_capture_id` 过滤响应
- 切换时清理旧请求或标记作废

**验收标准**:
- AC-P3-001-1: 详情响应包含 capture_id
- AC-P3-001-2: 切换 A→B 后，A 的响应被忽略
- AC-P3-001-3: 浏览器测试：快速切换 5 次，状态正确
- AC-P3-001-4: 提交时 capture_id 一致性验证

**验证方法**:
```typescript
// 自动化测试
test('capture switching ignores stale details', async () => {
  render(<CaptureWorkspace />)
  
  // 选择 Capture A
  selectCapture('capture-a')
  
  // 立即切换到 B（A 的详情还在加载）
  selectCapture('capture-b')
  
  // 等待所有请求完成
  await waitFor(() => expect(screen.queryByText('加载中')).not.toBeInTheDocument())
  
  // 验证显示的是 B 的内容，不是 A
  expect(screen.getByTestId('capture-id')).toHaveTextContent('capture-b')
})
```

---

### REQ-P3-002: Notes 列表服务端分页 [P1]

**来源**: A12, N04

**当前问题**:
- `manage/(workspace)/notes/page.tsx:15-18` 客户端过滤
- `notes.py:72-73` 默认返回 20 条
- 后续页无法访问，legacy 占首页导致假空态

**需求**:
- 服务端支持 `type` 过滤（note/blog）
- 服务端支持分页参数
- 客户端分页加载

**验收标准**:
- AC-P3-002-1: GET /api/notes?type=note&page=2 正确分页
- AC-P3-002-2: 21+ 笔记时可访问第二页
- AC-P3-002-3: legacy 笔记不影响当前笔记列表
- AC-P3-002-4: 空态正确显示（真实为空 vs 加载中）

**验证方法**:
```bash
# 创建 25 条笔记
for i in {1..25}; do
  curl -X POST /api/notes -d "{\"title\": \"Note $i\", \"note_type\": \"note\"}"
done

# 验证分页
curl "/api/notes?type=note&page=1&per_page=20" | jq 'length' # 期望 20
curl "/api/notes?type=note&page=2&per_page=20" | jq 'length' # 期望 5
```

---

### REQ-P3-003: 三条关键流程浏览器验证 [P1]

**来源**: DESIGN_RATIONALE_REVIEW 3.3, N04

**流程 1: Dashboard → Review → 再答 → 记录**
- 正常流程
- 无任务状态
- 失败重试
- 迟到返回保护
- 切换题目后状态隔离

**流程 2: Capture → 人工确认 → 草稿 → 正式**
- OCR 关闭时人工完成
- 请求乱序保护
- 保存失败保留输入
- 幂等转换

**流程 3: Notes → 编辑 → 保存 → 查询**
- 长标题、多页列表
- 未保存离开警告
- 保存失败重试
- 权限正确（公开/私有）

**验收标准**:
- AC-P3-003-1: 三条流程桌面端完整通过
- AC-P3-003-2: 三条流程移动端（390px）通过
- AC-P3-003-3: 录屏证据（每条流程 2-3 分钟）
- AC-P3-003-4: 关键断言数据库回读验证

**验证方法**:
- Playwright E2E 测试
- 真实浏览器手动测试
- 录屏保存到 evidence/

---

### REQ-P3-004: 八维视觉质量基线 [P1]

**来源**: DESIGN_RATIONALE_REVIEW 3.2

**八维标准**:
1. **排版**: 四级语义、行高、基线对齐
2. **留白**: 节奏、间距一致性
3. **视觉层级**: 主要动作突出
4. **色彩**: 语义 token、对比度
5. **动效**: 状态解释、时长合理
6. **微交互**: 提交保护、焦点管理
7. **响应式**: 390/768/1440 断点
8. **原创性**: 学习手稿编辑感

**验收标准**:
- AC-P3-004-1: 每维度独立检查 PASS
- AC-P3-004-2: 截图证据（桌面 + 移动）
- AC-P3-004-3: 对比度测试 ≥4.5:1（正文）
- AC-P3-004-4: reduced-motion 支持
- AC-P3-004-5: 触控目标 ≥44px

**验证方法**:
- 截图 + 标注
- Lighthouse 可访问性检查
- 对比度工具测量
- 真实设备测试

---

## Phase 4: 完整验收（N06）

### REQ-P4-001: 原计划验收矩阵 [P0]

**来源**: ROADMAP N06, Week/PR 退出条件

**必须覆盖**:
- 所有 P0 需求闭合
- 原五条 E2E 通过
- 类型门禁 PASS
- 前端 530+ 测试 PASS
- 后端完整测试 PASS

**验收标准**:
见 Phase 5 联合检查报告

---

## Phase 5: 前后端联合检查（强制）

### REQ-P5-001: 后端独立验证 [P0]

**必须通过**:
1. Schema 一致性验证
2. API 合同测试全覆盖
3. 业务不变量测试
4. 并发竞争测试
5. 数据持久化测试

**详见**: phase5-integration/backend-verification.md

---

### REQ-P5-002: 前端独立验证 [P0]

**必须通过**:
1. 组件状态隔离
2. 用户交互完整性
3. 视觉质量达标
4. 可访问性基线

**详见**: phase5-integration/frontend-verification.md

---

### REQ-P5-003: 集成验证 [P0]

**必须通过**:
1. 真实浏览器 E2E（三条流程）
2. 竞态条件测试
3. 错误处理完整性

**详见**: phase5-integration/integration-tests.md

---

## 非功能需求

### NFR-001: 性能基线

**目标** (Core Web Vitals):
- LCP ≤ 2.5s
- INP ≤ 200ms  
- CLS ≤ 0.1

**验收**: Lighthouse 报告 + 真实用户监控（如果部署）

---

### NFR-002: 可访问性

**目标**:
- ARIA 标签完整
- 键盘导航可用
- 读屏器可用（NVDA/VoiceOver 至少一个）
- 焦点管理正确

**验收**: axe DevTools 扫描 + 手动测试

---

### NFR-003: 浏览器兼容性

**目标**:
- Chrome 最新
- Firefox 最新
- Safari 最新
- 移动 Safari（iOS）
- 移动 Chrome（Android）

**验收**: BrowserStack 或真机测试

---

## 明确排除（本轮不做）

### EXCLUDED-001: 架构重构

- 不拆分微服务
- 不引入 Redis/RQ
- 不迁移到 monorepo
- 不更换认证机制

### EXCLUDED-002: 新功能

- 不实现持久 StudyPlan
- 不实现 KP Mastery
- 不实现每日 AI 计划
- 不实现后台 OCR 队列

### EXCLUDED-003: 生产操作

- 不连接生产数据库
- 不执行生产迁移
- 不部署到生产环境
- 本轮验证在隔离环境

---

## 风险与缓解

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| 数据合同修改引入新 bug | HIGH | 充分测试覆盖 + 回滚计划 |
| 视觉迭代时间超预期 | MEDIUM | 最小可接受标准 + 迭代停止条件 |
| 前后端联合测试失败 | MEDIUM | 独立验证先行 + 逐步集成 |
| 发现新的架构问题 | MEDIUM | 上报用户决策 + 范围调整 |
| 测试环境不稳定 | LOW | 隔离数据库 + 固定种子数据 |

---

## 验收总结

**成功定义**:
- 所有 P0 需求验收 PASS
- 所有 P1 需求验收 PASS 或有明确缓解
- P2 需求明确列入后续计划
- 前后端联合检查报告 ACCEPT
- 系统状态从 PARTIAL 晋升为 **VERIFIED_BASELINE**

**部分成功定义**:
- P0 需求有剩余但有明确计划
- P1 需求部分完成
- 联合检查报告 PARTIAL
- 明确标记 PARTIAL 与阻断原因

**失败定义**:
- P0 需求有未解决阻断
- 数据正确性问题未闭合
- 联合检查报告 REJECT
