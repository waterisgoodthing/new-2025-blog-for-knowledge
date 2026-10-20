# 当前运行证据

所有数据库写入仅在本轮新建 /tmp/pls-audit-20260927-pg 集群（127.0.0.1:55439）三个 astra_week4_quality_* 数据库；未连接现有业务库。主Agent执行。

| 验证 | 结果 | 原始日志 |
|---|---|---|
| frontend vitest | 70 files / 522 passed，Node26 | evidence/frontend-test.txt |
| tsc --noEmit --incremental false | exit0 | evidence/typecheck.txt |
| test:typecheck | exit0 | evidence/test-typecheck.txt |
| Node24 Next build | exit0 | evidence/build.txt |
| Node24 OpenNext build | exit0 | evidence/build-cf.txt |
| PG16 fresh upgrade 001..033 | exit0 | evidence/migration-upgrade.txt |
| pytest 全量无deselect | 922 pass /9 skip /2 warning /47 subtests | evidence/backend-test.txt |
| alembic check | exit255 metadata ownership drift | evidence/alembic-check.txt |
| 空库033→027→033 | exit0 | evidence/migration-empty-roundtrip.txt |
| 有数据库033 downgrade | 拒绝2个live challenge，预期fail-closed | evidence/migration-downgrade.txt |
| workerd smoke | 20/20 assets，23/23 checks | evidence/runtime-smoke.txt |
| Chromium E2E | 5/5 pass，含真实UI和后端读回 | evidence/e2e.txt |
| 学习KP继承probe | 断链复现，事务回滚 | evidence/probe-learning.txt |
| 多选再答probe | UI单选覆盖导致wrong，真实浏览器201 | evidence/probe-multiple-choice.txt |

不将本地结果视为remote CI/生产验收。PDF和报告检查待完成。

## 最终补验与验收

- Node24 frontend vitest补跑70文件522通过：evidence/frontend-test-node24.txt；消除初轮Node26与CI契约差异。
- 精确skip归因：evidence/skipped-tests.txt，35pass/9skip/6subtests；3项Week2旧库名前缀与统一guard合同不合，6项LSR03 opt-in环境缺省；未绕过保护。
- Legacy freeze：evidence/probe-freeze.txt，ASGI真实handler+隔离PG，合成admin依赖，200且folder变更；事务回滚。
- 独立审查PASS：workers/independent-review.md；它只接受审计报告，不宣称产品通过。
- PDF：28页；全部页面渲染为PNG并检查4张覆盖全部页的contact sheets，重点放大第14/20/28页表格；无裁切、重叠、缺字。边界扫描0异常，replacement字符0。evidence/pdf-qa/qa.json与render PNG留证。
- 初始2785个既有文件SHA256对比0变化：evidence/preservation-check.json。
- Markdown全33章、19PR及9个活跃Week路线的任务矩阵、Future/不做项/三层Roadmap/十问覆盖检查见completion-checklist.md。

- 最终结构/链接/hash/PDF检查：evidence/final-checks.json；33章节、19PR、9周、6Worker报告、broken_links=0；git diff --check exit0。
- 临时backend18401、workerd18487已关闭；本轮新PG集群pg_ctl no server running，保留隔离测试数据目录供复查（未删除既有数据）；cleanup.txt记录正常停止。
