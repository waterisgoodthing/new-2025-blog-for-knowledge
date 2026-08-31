# CLEANUP 交接提示

当前无需外部代理；CLEANUP 已完成。

后续执行者必须先读取本目录全部 workflow 文档，严格区分：

- 已授权删除的 `src/app/workspace/`；
- 只读日常库 `localhost:5432/blog_db`；
- 可写且必须销毁的临时 clone；
- 未授权的部署、推送、日常库 migration 和认证改动。

如后续接手：

- 不得从 CLEANUP PASS 推断日常库已升级到 025。
- 测试 warning 与登录头像 LCP 提示已进入 `next-requirements.md`。
- 删除原型和临时 DB 根可从 macOS 废纸篓恢复，但其中包含敏感 dump，
  不应长期保留或提交。
