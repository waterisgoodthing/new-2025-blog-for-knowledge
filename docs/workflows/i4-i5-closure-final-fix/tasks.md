# 任务清单

状态：`COMPLETE / PASS / FINAL-FIX-VERIFIED (2026-07-24)`

> 需明确批准本任务清单后才开始实现。批准不包含迁移、部署、推送或源库写入；只允许使用已存在且已确认的 022 隔离目标。

- [x] FINAL-01 修复后端 lifecycle 测试的 asyncpg/event-loop 隔离；保留 commit、rollback、close 与异常后恢复语义。commit/rollback/close/recovery 已合并到单一 `asyncio.run()`，定向测试通过。
- [x] FINAL-02 将 learning、activity、storage 三类独立故障注入固化为三个回归测试。三个独立场景均通过，并分别断言其他区块与系统健康映射。
- [x] FINAL-03 移除 `maximum-scale` / `user-scalable=no`，补充 viewport 元数据与移动端可缩放检查。新增 viewport 契约测试通过。
- [x] FINAL-04 只读确认真实隔离数据库为 Alembic `022 (head)`，重跑四文件后端组合套件并保存完整输出。目标为 `127.0.0.1:55435/pls_v2_i4_target`，`current=heads=022`；四文件组合 `17 passed`，未执行迁移。
- [x] FINAL-05 重跑前端完整定向套件（26 项）、TypeScript、生产构建和移动端浏览器验收。7 个文件、26 项通过；TypeScript、build、390×844/1280×800/1440×900 与键盘检查通过。
- [x] FINAL-06 同步 closure-fix-2 与本批次 README/tasks/validation 的测试数量、状态、revision、证据链接和阻断结论。旧 020 阻断已改为历史运行时说明，最终证据指向既有 022 隔离目标。
- [x] FINAL-07 做最终代码质量、范围和闭环审查；后端 17 项、前端 26 项、类型、构建、Python compileall、diff check 与浏览器证据均已记录，状态为 `COMPLETE / PASS`。
