# I 系列剩余任务：简化路径执行指令

**决策日期**：2026-07-29

**决策**：批准方案 A（简化路径），终止完整 C6-C9 影子迁移实现
**理由**：系统规模（121 rows）不需要零停机双写架构，直接验证当前 024 权威完整性更高效

---

## 背景

- ✅ C0-C5 已完成：owner manifest + 020→024 upgrade + Git 权威收口（commits 2c7adcc + 0205272）
- ✅ Source DB 在 revision 024，migration 021-024 已 tracked
- ✅ C1 manifest 121/121，aggregate `b40b109a0a1a7eca9b633a11503f8327c8c051fa0b4f05fb0efa04a79089adb6` 在 024→020 投影下保持不变
- 🚫 原 C6 BLOCKED：缺少 shadow target 基础设施（决策为**不实现**，改为简化验证）

---

## 你的任务序列

按顺序执行以下增量，每个完成后立即更新 `validation.md` 并勾选 `tasks.md`。

### **C6-简化：最终数据完整性审计**

**目标**：在 live source 024 上执行只读完整性检查，证明 schema 权威统一且数据无损。

**范围**：
1. **重用现有证据**：`c1-post-upgrade-verification.json` 已证明 121/121 rows、aggregate 不变
2. **新增 FK 完整性检查**：
   - mistakes → questions (question_id)
   - mistakes → draft_items (source_draft_item_id)
   - review_items → mistakes (target_id where target_type='mistake')
   - review_records → review_items (review_item_id)
   - attachment_links → attachments/mistakes/questions (attachment_id, target_id)
   - capture_items → attachments (source_attachment_id)
   - **使用 C1 verifier 中已有的 `_relationship_orphans()` 函数**
3. **Backfill correctness**（024 新增字段）：
   - `notes.revision`：验证所有 notes 的 revision ≥ 1（C5 已回填）
   - `attachments.display_name`：验证非空且与 filename 一致（C5 已回填）
   - `attachments.folder_id`：允许 NULL（新字段，未分配文件夹）
4. **Source facts snapshot**：
   - Table counts（12 tables）
   - Schema version（024）
   - Extensions（pg_trgm, plpgsql）
   - User count（8 users, 1 canonical owner）

**输出**：`assets/c6-final-integrity-audit.json`，包含：
```json
{
  "audit_date": "2026-07-29T...",
  "source_revision": "024",
  "manifest_verification_reused": "c1-post-upgrade-verification.json",
  "manifest_passed": true,
  "fk_integrity": {
    "mistake_question": 0,
    "mistake_draft": 0,
    "review_item_target": 0,
    "review_record_item": 0,
    "attachment_link_attachment": 0,
    "attachment_link_target": 0,
    "capture_attachment": 0
  },
  "fk_orphan_count": 0,
  "backfill_verification": {
    "notes_revision_null": 0,
    "notes_revision_min": 1,
    "attachments_display_name_null": 0,
    "attachments_display_name_mismatch": 0
  },
  "source_facts": {
    "table_counts": { "notes": 13, "mistakes": 3, ... },
    "extensions": ["pg_trgm", "plpgsql"],
    "canonical_owner": "4c503215-b158-4162-b472-79df8289ed0a",
    "admin_count": 4,
    "total_users": 8
  },
  "passed": true,
  "conclusion": "PASS"
}
```

**不做**：
- 不创建 shadow target DB
- 不写入 source（仅只读查询）
- 不实现 upsert/delta/tombstone tooling

**退出门槛**：
- `fk_orphan_count = 0`
- `backfill_verification` 所有 null/mismatch = 0
- `passed = true`

**实现提示**：
- 可以复用 `manifest_tool.py` 中的 `_relationship_orphans()` 和 `_psql()` 函数
- 新建 `assets/integrity_audit.py` 或直接在 manifest_tool.py 添加 `audit` 子命令

---

### **C7-简化：024 完整恢复验证**

**目标**：从 C5 的 024 restore point 恢复到全新隔离 DB，证明备份可用于灾难恢复。

**范围**：
1. **隔离 DB 创建**：`i_series_c7_restore_verify_[timestamp]`，owner=`blog_user`
2. **Restore 执行**：
   - 从 `/Users/limengyang/Backups/2025-blog-public/20260728-c5-source-024/database.dump` 恢复
   - 解压并恢复 `backend-uploads.tar.gz` 和 `public-images-pictures.tar.gz` 到临时目录
3. **验证项**：
   - Alembic current = 024
   - Table counts 与 live 一致（notes=13, mistakes=3, ...）
   - 121-row manifest 在 restored DB 上重新验证（使用 024→020 投影）
   - Aggregate SHA-256 = `b40b109a0a1a7eca9b633a11503f8327c8c051fa0b4f05fb0efa04a79089adb6`
   - FK orphans = 0
   - Backfill correctness（notes.revision, attachments.display_name）
   - `validate_database_readiness()` = PASS（使用 candidate runtime）
   - `alembic check` = clean
4. **清理**：
   - Drop 隔离 DB
   - 移动临时附件目录到 `~/.Trash/`（不删除）
   - 保留 C5 backup（不动）

**输出**：`assets/c7-restore-verification.json`，包含：
```json
{
  "restore_date": "2026-07-29T...",
  "source_backup": "20260728-c5-source-024",
  "backup_sha256_verified": true,
  "restored_db": "i_series_c7_restore_verify_20260729_HHMMSS",
  "restored_revision": "024",
  "table_counts": { "notes": 13, ... },
  "manifest_verification": {
    "passed": true,
    "aggregate_match": true,
    "fk_orphans": 0
  },
  "backfill_verification": {
    "notes_revision_null": 0,
    "attachments_display_name_null": 0
  },
  "readiness_check": "PASS",
  "alembic_check": "No new upgrade operations detected",
  "cleanup_completed": true,
  "passed": true,
  "conclusion": "PASS - 024 backup is valid for disaster recovery"
}
```

**不做**：
- 不写入 live source
- 不服务应用流量（隔离验证）
- 不修改 C5 backup

**退出门槛**：
- Restored DB 所有验证 PASS
- Aggregate match = true
- Cleanup 完成（隔离 DB 已删除）

---

### **C8/C9：标记为 SKIPPED**

更新 `tasks.md`：
```markdown
- [ ] C8：~~实际权威切换并观察~~ → **SKIPPED**（2026-07-29 决策：单一 source 架构无需切换）
- [ ] C9：~~旧写停用与 Legacy 只读归档~~ → **SKIPPED**（2026-07-29 决策：source 即唯一权威，无 Legacy）
```

更新 `risk-register.md`：
- I-RISK-P0-07 状态改为 `RESOLVED - C6-C9 改为简化验证，不实现 shadow target`
- 新增备注："影子迁移基础设施因系统规模（121 rows）不适用零停机架构而跳过。"

---

### **C10：F-01 最终验证**

**目标**：完成 I12-01 定义的全量验收，解除 F-02 的质量阻塞项。

**范围**：

#### 1. **管理员真实会话（非 AUTH_BYPASS）**
- 在 `.env` 设置 `AUTH_BYPASS=false`
- 启动 backend（应能正常启动，因 C5 已验证 readiness）
- 使用真实 passkey/password 登录管理员账户
- 验证可以访问 `/manage/` 路由
- **证据**：截图或日志片段，显示 `AUTH_BYPASS=false` + 成功登录

#### 2. **权限矩阵**
- 匿名用户：可访问 `/api/notes`（公开列表）、不可访问 `/api/notes/[slug]/edit`
- 失效 token：401 Unauthorized
- 非 admin 用户：不可访问 `/manage/`（若有权限检查）
- **证据**：`assets/c10-permission-matrix.json`，列出每个场景的 HTTP status

#### 3. **024 恢复验证（已在 C7 完成）**
- 重用 C7 的 `c7-restore-verification.json`
- 确认 C7 结论为 PASS

#### 4. **完整失败态**
- 404：访问不存在的 note slug
- 401：无 token 访问受保护 API
- 403：非 admin 访问管理员 API（如果有）
- 500：故意触发（可选，或跳过此项说明"无可控 500 触发器"）
- **证据**：`assets/c10-failure-states.json`

#### 5. **三尺寸浏览器测试**
使用 Browser Preview（如果可用）或手动测试：
- Mobile (375x812)：导航可用、无横向滚动
- Tablet (768x1024)：布局适配
- Desktop (1280x800)：完整功能
- 键盘导航：Tab 可遍历交互元素
- **证据**：截图或文字描述，保存到 `assets/c10-browser-testing.md`

#### 6. **Frontend 测试修复（58/58）**
- 调查 `static-placeholders.test.tsx` 的 Capture case 失败原因
- 修复 App Router fixture 或跳过该测试（并在 F-02 中标注）
- 目标：`npm test` = 58/58 PASS
- **证据**：测试输出日志

#### 7. **代码质量**
- `npx tsc --noEmit`：PASS（C5 已验证）
- `npm run build`：PASS（C5 已验证）
- Backend `python3 -m compileall backend/`：PASS（C5 已验证）
- **证据**：重用或重新运行并记录到 `validation.md` C10

#### 8. **独立交叉验证**
- 在新的终端 session 或不同目录 clone repo
- 重跑 manifest verification：`python3 manifest_tool.py verify --manifest=... --report=c10-cross-verify.json`
- 验证 aggregate 仍为 `b40b109a...89adb6`
- **证据**：`assets/c10-cross-verification.json`

**输出**：更新 `validation.md` 添加 C10 章节，汇总所有证据文件。

**退出门槛**：
- 所有验证项 PASS 或明确标注 SKIPPED（并说明理由）
- Frontend 测试 ≥ 57/58（如果 58th 无法修复，需在 F-02 中说明）

---

### **C11：F-02 部署资格审查（更新）**

**目标**：基于简化路径重新评估部署资格。

**更新 `f02-deployment-eligibility.md`**：

| 检查项 | 状态 | 证据 |
|---|---|---|
| C1 owner manifest | PASS | 121 rows，dual-query hash/count/relationship gates=0 |
| 020→024 artifact/source upgrade | PASS | C3 artifact, C5 current=head=024, check clean |
| 024 restore | PASS | C7 restore verification, aggregate match |
| ~~E-05 shadow migration~~ | SKIPPED | 简化决策：单一 source 架构 |
| ~~E-06 switch/reverse delta~~ | SKIPPED | 无 shadow target |
| F-01 完整验证 | PASS/PARTIAL | C10 结果（待执行） |
| Git authority | PASS | commits 2c7adcc + 0205272, migrations tracked |
| Frontend test suite | PASS/FAIL | C10 结果（目标 58/58） |
| Production runtime | FAIL | Public API tunnel backend 无 listener（不部署边界仍生效） |

**结论**（根据 C10 结果调整）：
- 若 C10 全 PASS + frontend 58/58：`ELIGIBLE (但不部署，因 production runtime 未启用)`
- 若仍有失败项：`NOT ELIGIBLE / DO NOT DEPLOY`，列出阻塞项

**不执行部署、push、生产配置修改。**

---

### **C12：F-03 最终报告**

**目标**：更新 `f03-final-status-report.md`，记录完整状态。

**更新内容**：

1. **架构决策**：
   - "影子迁移（C6-C9）因系统规模（121 rows，单用户）改为简化验证路径"
   - "Source `blog_db` 024 为唯一权威，无 target/Legacy"

2. **10 个状态维度**（更新）：
   - MVP 基础：COMPLETE（C5 024 schema 统一）
   - 产品化：PARTIAL（Phase 1.0 未完成，但不在本次范围）
   - 知识工作区：COMPLETE（I7/I8 功能已实现）
   - AI-OCR：COMPLETE（I9 governance）
   - 备份恢复：PASS（C4/C5/C7 验证）
   - ~~Dry-run/权威切换/Legacy~~：SKIPPED（简化决策）
   - 部署资格：ELIGIBLE/NOT ELIGIBLE（基于 C11）
   - 实际部署：NOT DEPLOYED（按计划）

3. **残余风险**：
   - Frontend 测试若仍 57/58，需说明 Capture fixture 问题
   - Production runtime 未启用（tunnel → localhost:8000 无 listener）

4. **审批历史**：
   - C0-C5：2026-07-28 授权，2026-07-29 Git 收口完成
   - C6-C9 简化：2026-07-29 批准
   - C10-C12：（待完成后填写）

5. **Git commits**：
   - `2c7adcc`：83-file artifact + 16 workflow docs
   - `0205272`：documentation ledger, risk closure
   - （C6-C12 完成后的新 commits）

**不 push、不发布。本地留档。**

---

## 执行顺序

1. **立即开始 C6-简化**（只读审计）
2. 完成后执行 **C7-简化**（restore 验证）
3. 更新 **tasks.md**，标记 C8/C9 为 SKIPPED
4. 执行 **C10**（F-01 验证）
5. 基于 C10 结果更新 **C11**（F-02）
6. 完成 **C12**（F-03 最终报告）
7. **全部完成后**，commit 一次：`docs: complete I-series simplified path C6-C12`

---

## 约束条件（不可违反）

1. **只读原则**：C6/C7/C10 对 live source 仅只读查询
2. **不改 C1 manifest**：保持 revision 020、aggregate 不变
3. **不改 C3-C5 artifacts**：out-of-repo backups 不动
4. **不 push/部署/改生产配置**
5. **隔离清理**：C7 的临时 DB 必须删除

---

## 成功标准

- C6/C7 输出 JSON 证据文件，所有 `passed = true`
- C10 所有验证项 PASS 或合理 SKIPPED
- C11 给出明确 ELIGIBLE/NOT ELIGIBLE 结论
- C12 完整记录决策与状态
- 全程无 live source 写入（除了只读查询）

---

## 开始

从 **C6-简化** 开始执行。先创建 `assets/integrity_audit.py`（或在 manifest_tool.py 添加 `audit` 子命令），然后运行并生成 `c6-final-integrity-audit.json`。
