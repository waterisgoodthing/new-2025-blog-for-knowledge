# Requirements：Test Teardown Cleanup

## R1 范围

本任务只处理 backend test isolation 与 teardown，影响 shared infrastructure、mistakes、review、attachments 测试。不得改变业务 API、schema、model、migration 或生产事务语义。

## R2 数据安全

- 不得默认测试数据库为空。
- 不得对未验证为专用测试库的数据库执行全表清理。
- 测试断言必须限定到本测试创建的数据。
- 如确需 destructive cleanup，必须先增加明确 test-environment guard，并更新设计后重新申请批准。

## R3 Session 清理

每个数据库测试结束后，无论成功、失败或 setup 部分失败，都必须：

- rollback 未提交 transaction；
- close session；
- 不留下未归还连接。

## R4 Engine 清理

- 必须用复现证据判断 engine dispose 的正确边界。
- 不得让共享 pooled connection 跨已关闭事件循环复用。
- 不得为了测试修改生产 engine 行为，除非另行审批。

## R5 文件清理

Attachment 测试创建的临时目录和文件必须在 teardown 后不存在；清理应在测试失败时仍执行。

## R6 确定性

以下运行方式都必须通过，且不得出现 asyncpg connection/event-loop teardown 警告：

- mistake/review 定向测试；
- attachment 定向测试；
- 两文件正序与逆序；
- mistake/review 文件连续两次；
- 全量 backend tests。

## R7 验证记录

所有验证命令、结果、警告和未解决项必须记录到 `validation.md`。若全量测试存在与本任务无关的预置失败，必须列出首个相关失败并证明本任务没有新增失败。

## R8 变更纪律

- 优先修改测试与测试支持代码。
- 不新增大依赖。
- 不进入 Batch 11。
- 每完成一个 `tasks.md` 项必须立即勾选并记录证据。
