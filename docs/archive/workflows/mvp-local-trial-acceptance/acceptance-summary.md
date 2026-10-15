# MVP 第一阶段项目验收摘要

## 结论

**Conditional pass / 有条件通过。**

MVP 第一阶段核心学习链路、附件链路和公开边界已经通过真实本地私有样例验证，可以进入项目演示和日常使用观察。该结论不是“所有环境完全通过”：`LT-ISSUE-002` 仍需后续独立处理。

### P0-15 更新

现场只读演示曾发现 `DEMO-ISSUE-001`：匿名 `/mistakes` 被 307 重定向到 `/manage/mistakes`。P0-16 删除该错误 redirect 后，P0-17 再次演示确认 `/mistakes` 匿名列表可访问，`/mistakes/review` 仍受保护。该问题现已关闭。

P0-18/P0-19 随后修复并验证 `LT-ISSUE-002`：禁用账号密码登录现在返回 401，不再返回 500。当前 MVP 第一阶段验收结论为 **pass**；`LT-ISSUE-001` 仅作为非目标 localhost Passkey 兼容问题归档。

## 已验证

```text
subject
→ knowledge point
→ question draft
→ question
→ mistake draft
→ mistake
→ review item
→ review record
→ attachment upload
→ attachment link
→ attachment read
```

- 3 条人工转述样例完成主链路。
- 3 个 review item 均提交过 review record。
- 1 个无敏感信息本地附件完成上传、关联、读取和内容一致性验证。
- 未登录公开页面可访问，未暴露管理操作或私有样例。
- 未授权管理 API、复习、附件和写入操作保持保护。
- Batch 7 自动化验证、TypeScript、生产构建和 Alembic 检查已通过。

## 数据与环境

- Alembic：`020 (head)`。
- 当前数据 counts：`notes=13`、`subjects=1`、`knowledge_points=3`、`questions=3`、`mistakes=3`、`review_items=3`、`review_records=4`、`attachments=1`、`attachment_links=1`。
- Batch 7 未执行 migration、数据迁移、部署或外部能力调用。
- 详细对象 ID 和证据见 [trial-record.md](./trial-record.md) 与 [validation.md](./validation.md)。

## 条件项与风险

- `LT-ISSUE-002`：禁用临时管理员后，原密码登录返回 500，预期为 401；账号权限已撤销，旧会话返回 403，不阻塞主链路，但需要独立 Auth Error Handling Cleanup。
- `LT-ISSUE-001`：localhost Passkey RP/Origin 不匹配，已归档为非目标环境问题。
- 当前 Git 工作区包含前序批次脏改动；演示前不得把未审查改动误称为本阶段验收证据。

## 未验证或不在本阶段

- 云部署、生产环境验收、AI/OCR、BKT、完整练习、Search、Analytics、对象存储和多用户权限系统。
- 现场重新写入数据、重新创建管理员或修复条件项。

## 验收建议

演示时使用只读优先路径：先展示公开读取，再展示已授权管理工作区和既有验收对象，最后展示本摘要、Batch 7 validation 和条件项。不要在演示中暴露密码、token、私钥或敏感附件。
