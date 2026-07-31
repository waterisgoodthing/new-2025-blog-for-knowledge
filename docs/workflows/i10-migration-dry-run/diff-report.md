# I10 差异报告

- 已建立只读静态/数据库来源清单和 SHA-256 哈希；未把个人正文、密钥、token 或数据库 dump 写入仓库。
- 已记录目标字段映射和冲突原则：Note/Mistake/Question/Review 继续由各自模型拥有，文件节点不能替代正式学习对象；稳定 ID/slug 冲突必须人工裁决。
- `DRY_RUN_READY` 已于 2026-07-31 更新为 PASS：canonical owner 明确，
  immutable manifest 121/121，隔离 sidecar backfill、owner FK、关系、
  hash、024→025、Alembic check 和销毁均通过。
- 未执行源库写入、生产迁移或权威切换；技术 dry-run 只写入临时 clone，完成后已销毁。
- owner 覆盖按表记录在 [owner-coverage.md](owner-coverage.md)；映射来自用户
  批准的单管理员策略，没有把 `created_by`、slug 或路径当作推断依据。
- E-05/E-06 仅更新为 `READY / NOT AUTHORIZED`，未执行影子迁移或切换。
