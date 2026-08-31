# I11 差异报告

I11 E-05 已在用户明确授权下完成隔离执行。新增 shadow/delta 安全工具、4 个
fixture 测试和机器可读对账证据；一次性 shadow 从 source 024 恢复后升级至
025，完成 123/123 ledger、121-row immutable v1 + 2-row delta、单 owner、
零 orphan、双扫描与幂等 replay 验证。sidecar、shadow 与隔离测试库均已销毁，
source 前后 revision/count/hash/rows 一致。

E-05 本身未接 runtime。2026-08-01 E-06 随后在独立授权内完成：新鲜备份与
隔离恢复、source 025、稳定 target、首次切换/观察、forward/reverse delta、
回切、最终重切、Legacy 只读归档和临时身份清理。最终 authority=`blog_v2`；
Legacy `blog_db` 未删除且只读。清理后 123/123、零 delta，I11-04 独立 SQL/hash、
owner、关系、附件和连接身份 PASS。应用部署和 Git push 均未执行。
