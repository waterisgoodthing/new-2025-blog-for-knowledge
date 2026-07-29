# I10 差异报告

- 已建立只读静态/数据库来源清单和 SHA-256 哈希；未把个人正文、密钥、token 或数据库 dump 写入仓库。
- 已记录目标字段映射和冲突原则：Note/Mistake/Question/Review 继续由各自模型拥有，文件节点不能替代正式学习对象；稳定 ID/slug 冲突必须人工裁决。
- `DRY_RUN_READY` 未通过：owner 归属及 owner backfill 责任 UNKNOWN；技术 clone 的 Alembic 020→024、对账、回滚重放和销毁均已有证据。
- 未执行源库写入、生产迁移或权威切换；技术 dry-run 只写入临时 clone，完成后已销毁。
- owner 覆盖和待裁决队列按表记录在 [owner-coverage.md](owner-coverage.md)；没有引入管理员或 `created_by` 的隐式映射。
