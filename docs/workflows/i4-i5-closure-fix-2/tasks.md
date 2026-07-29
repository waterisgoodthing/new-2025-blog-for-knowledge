# 任务清单

状态：`COMPLETE / PASS / FINAL-FIX-VERIFIED (2026-07-24)`

> 只有用户明确批准本文件或指定任务批次后，才能执行下列实现任务。批准不包含迁移、部署、推送、源库写入或生产操作。

- [x] CF2-01 固化共享偏好契约与学习行动区块规则：后端 schema、前端类型/纯函数、设置页即时校验和错误提示。后端 Schema、前端契约与 022 目标 HTTP 组合验证通过。
- [x] CF2-02 接入 Dashboard 偏好渲染：按 `section_order` 排序并应用 `hidden_sections`，非法/缺失偏好回退默认值，保证学习行动区块可见。Dashboard 行为测试通过（10 项）。
- [x] CF2-03 修正 Dashboard `empty` 与系统健康状态映射，并保持 learning/activity/storage 局部失败隔离。状态映射与三类独立故障回归测试通过；022 目标后端组合测试通过。
- [x] CF2-04 补齐后端测试：局部失败、正常 commit、empty 健康映射、rollback/close 后恢复、偏好 PUT 后 GET 刷新一致。四文件组合共 17 项通过，lifecycle 测试已隔离到单一事件循环。
- [x] CF2-05 补齐前端测试：真实区块 DOM 顺序/隐藏、学习行动保护、empty 文案和保存后刷新生效。最终定向套件 26 项通过。
- [x] CF2-06 重新采集管理员浏览器证据：设置偏好、刷新 Dashboard，验证隐藏/排序实际生效；记录 390×844、1280×800、1440×900 与键盘关键路径。证据与截图已写入 validation.md；浏览器部分使用受控 API fixture，后端 022 另有真实组合套件证据。
- [x] CF2-07 执行定向测试、TypeScript/Python 编译、必要构建与 diff 检查，回写 validation.md，并据实际输出修正文档测试数量。前端 26/26、后端组合 17/17、TypeScript、Python compileall、build、diff check 通过。
- [x] CF2-08 完成代码质量与范围复核；最终状态 `COMPLETE / PASS`。022 隔离目标 `current=heads=022`，未执行迁移、部署、推送或源库写入。
