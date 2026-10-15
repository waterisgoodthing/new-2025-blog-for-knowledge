# I5 准备进度

| 时间 | 事项 | 状态 |
| --- | --- | --- |
| 2026-07-22 | 复用 I4 工作区并建立 I5 准备范围 | 完成 |
| 2026-07-22 | 检查 I5 现有要求、公开 site-settings 与管理入口 | 完成；已确认 public site-settings、legacy 页面设置、workspace 占位页与 User 模型边界 |
| 2026-07-22 | 形成 I5 设计、需求和任务清单 | 完成；已明确私有 profile 推荐方案、权限、失败态、恢复与三尺寸验收 |
| 2026-07-22 | 用户批准 I5 任务清单 | 完成；批准 I5-01 至 I5-10 |
| 2026-07-22 | I5-01 公开/私有边界与 ADR | 完成；见 ADR-I5-01 |
| 2026-07-22 | I5-02 schema authority 与 migration 方案 | 完成；采用独立 `admin_profiles`，目标 revision `022` |
| 2026-07-22 | I5-03 私有 profile schema/service/router/client 与契约 | 完成；后端 profile 4 项、前端契约测试已通过 |
| 2026-07-22 | I5-04 `/manage/settings` 私有设置表单 | 完成；设置组件 3 项测试通过 |
| 2026-07-22 | I5-05 Dashboard 欢迎/时区与 profile 降级 | 完成；Dashboard 9 项 overview 测试通过 |
| 2026-07-22 | I5-06 公开/私有隔离与匿名失效会话验证 | 完成；公开网络未请求 profile，匿名/失效 profile 为 401，公开 payload 无私有字段 |
| 2026-07-22 | I5-07 定向测试与代码质量检查 | 完成；前端 22 项、后端 11 项、TypeScript、Python 编译、Alembic check、diff check 通过 |
| 2026-07-22 | I5-08 隔离 migration cycle | 完成；`021 → 022 → 021 → 022`，最终 revision `022`，后续查询恢复 |
| 2026-07-22 | I5-09 三尺寸与键盘浏览器证据 | 完成；资产已保存至 `assets/i5-preparation/` 并链接 validation |
| 2026-07-22 | I5-10 残余风险、归档与文档统一 | 完成；I5 `COMPLETE / PASS`，I6 需单独审批 |

## 本次错误与处理

| 错误 | 处理 |
| --- | --- |
| 首次按技能别名读取 `SKILL.md` 的路径不存在 | 根据技能根目录重新定位到 `/Users/limengyang/.agents/skills/ok-skills/planning-with-files/SKILL.md`，随后完整读取 |
| 使用未加引号的含括号前端路径进行 shell 读取，触发 zsh `no matches found` | 保留路径事实不变，后续对 `src/app/(home)/...` 统一加引号 |
| I5 首个红灯测试在实现前收集失败：`ModuleNotFoundError: app.models.admin_profile` | 按 TDD 预期先创建模型/契约，再回到同一测试进入 green |
| 首次路由测试假设 GET/PUT 合并为同一 FastAPI route，导致 route 断言失败；实际框架为两个 route | 将测试改为分别检查 GET 与 PUT，保持公共路由权限断言 |
| I5-08 首次 `alembic check` 发现 model 使用 JSON、migration 使用 JSONB，且 user_id 索引命名不一致 | 将 model 对齐为 PostgreSQL JSONB，并移除重复自动索引；重新执行 downgrade/upgrade/check |
| 使用未转义反引号查询文档 revision，shell 将 ``021`` 当作命令执行 | 后续文档搜索统一使用单引号或转义反引号；未影响仓库文件 |
