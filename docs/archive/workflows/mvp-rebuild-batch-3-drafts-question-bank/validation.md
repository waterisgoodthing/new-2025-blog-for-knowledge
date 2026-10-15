# Batch 3 验证记录

## 当前状态

执行与验证完成；用户已确认 Batch 3 关闭并允许进入 Batch 4 workflow 准备。

## P0-01 TDD、迁移与数据门禁

### 审批

用户于 2026-07-03 明确批准执行 Batch 3 tasks。

### TDD RED

第一条行为：选择题草稿必须 trim 题干与选项，且选择题不得提交空 options。

```text
ModuleNotFoundError: No module named 'app.schemas.question'
1 error during collection
```

失败原因与预期一致，尚未创建实现。

### Alembic 与目标表

```text
current: 011 (head)
heads: 011 (head)
target_tables_present: 空
```

`draft_items`、`question_drafts`、`questions`、`question_sources` 均未被
`create_all` 提前创建，不存在 Batch 2 同类迁移漂移。

### 旧数据基线

```text
notes: blog=1, mistake=5, note=7
admin_sessions=18
passkey_credentials=1
audit_logs=84
netease_api_configs=1
music_source_rules=11
managed_content_entries=5
subjects=0
chapters=0
knowledge_points=0
knowledge_point_links=0
```

### 备份与恢复前提

- 仓库外备份：`/tmp/blog-db-pre-batch3.dump`
- 权限：600
- `pg_restore --list`：通过
- 仅在 012、schema、旧数据和完整验收均通过后删除。

## P0-02 模型与 Alembic 012

- 新增 4 张独立表：`draft_items`、`question_drafts`、`questions`、
  `question_sources`。
- 复用既有 `subjects` 外键与 `knowledge_point_links`，没有修改 Note 模型。
- 执行：`011 -> 012` 正常完成；`alembic current` → `012 (head)`。
- 重复 `alembic upgrade head` → 通过，无新增或破坏行为。
- Schema inspection：
  - draft_items：12 列、2 索引、1 FK、5 check
  - question_drafts：12 列、2 索引、2 FK、2 check
  - questions：14 列、2 索引、1 FK、5 check
  - question_sources：6 列、2 索引、1 FK、1 check
- 旧 Note 数量保持 `blog=1, mistake=5, note=7`。
- `py_compile` 对 model 与 migration 通过。

## P0-03 schemas 与 service

按纵向 TDD 逐条完成：

1. 选择题 options 合同：RED 为缺少 schema；GREEN 后 trim、去空、去重且至少 2 项。
2. manual draft + taxonomy link：RED 为缺少 `draft_service`；GREEN 后统一 item 与
   类型化草稿同事务创建。
3. 乐观锁：RED 为缺少 update；GREEN 后旧 version 返回 domain conflict。
4. 幂等转换：RED 为缺少 convert；GREEN 后重复请求返回同一 Question，并保留
   `source_type=manual` 与 Draft UUID。
5. 拒绝门禁：RED 为缺少 reject；GREEN 后 rejected 草稿不能转换。
6. 正式题目：RED 为缺少 update/archive；GREEN 后 version 防覆盖，DELETE 语义为归档。

最终：

```text
backend/tests/test_question_draft_service.py: 6 passed
```

`py_compile` 对 schema、draft service、question service 通过。转换顺序为行锁 →
version/状态校验 → Question → manual source → knowledge links → converted target，
由同一 AsyncSession 事务提交或回滚。

## P0-04 thin admin routers 与权限

- 注册 `/api/admin/drafts` 与 `/api/admin/questions`。
- 全部路由使用 router 级 `Depends(get_current_admin)`；create 路由复用同一缓存依赖
  取得 `created_by`。
- router 只映射 domain error：404 not found、409 conflict、400 validation；
  Pydantic 字段错误为 422。
- 路由/服务定向测试：`8 passed`；`compileall app main.py` 通过。
- 匿名 HTTP：
  - `GET /api/admin/drafts` → 401
  - `GET /api/admin/questions` → 401
  - `GET /api/admin/questions/{uuid}` → 401
- OpenAPI：存在 draft convert POST；不存在直接 question POST。
- 首次 HTTP 检查的首条失败为 `zsh: command not found: curl`，没有请求发出；
  改用系统绝对路径 `/usr/bin/curl` 后上述检查通过。

## P0-05 前端合同

- 新增 `src/lib/api/drafts.ts` 与 `questions.ts`，显式定义枚举、DTO、version 与操作。
- Question 只有 list/get/update/archive；客户端没有直接 create。
- Draft 提供 list/create/get/update/reject/convert。
- `KnowledgePointMultiSelect` 复用 Batch 2 active knowledge points，按 subject 过滤。
- `npx tsc --noEmit --pretty false` → 通过，无 TypeScript 错误。

## P0-06 管理页面真实浏览器验收

- 隔离环境：后端 8001、前端 2026；未终止用户已有 8000/2025 进程。
- 使用一次性 `temp-admin`，复用旧 `/manage` 登录体系与 workspace AuthGate。
- 真实流程：
  1. 创建 `Batch3 浏览器科目` 与 `Batch3 验收知识点`。
  2. 在 `/manage/drafts` 手工创建题目草稿。
  3. 草稿保存后从 v1 变为 v2，并绑定正式 KnowledgePoint。
  4. 点击确认入库后跳转唯一正式 Question 详情。
  5. 编辑解析为 `Batch3 正式题目解析`，刷新后仍存在。
  6. 归档正式题目后返回题库列表，没有物理删除 UI。
- 移动端：390×844 下 `scrollWidth === clientWidth === 390`。
- 浏览器 console error：0。
- 浏览器工具首次读取 ARIA snapshot 遇到缓存插件版本兼容错误；按技能故障恢复说明
  重连同一 in-app browser，并使用其受支持的 visible DOM/locator API 完成全部交互。

## P0-07 迁移、权限、兼容与清理

- 重复 convert HTTP → 200，返回与首次相同 Question UUID。
- DB 对账：该 draft 对应 `questions=1`、`question_sources=1`，确认幂等。
- 独立拒绝草稿：reject HTTP → 200，状态 `rejected`。
- 匿名 `GET /api/admin/drafts` → 401。
- `GET /api/public/questions` → 404，确认没有新增 public Question API。
- Alembic current → `012 (head)`；重复 upgrade 通过。
- 后端回归：Question/Draft + routes + taxonomy + temp admin → `15 passed`。
- TSC → 通过；`npm run build` → 通过，32/32 页面生成，新 drafts/questions
  详情路由正确识别为动态路由。
- 构建仅出现既有 baseline-browser-mapping 过期与 Node deprecation warning。
- 公开 `/notes`、`/mistakes` 均正常，浏览器 console error=0；后端仍有
  `AGENTS.md` 已知的公开 mistakes 请求管理员 review/weak-points API 403 噪音，
  本批未跨范围修复。
- 清理后 `draft_items/question_drafts/questions/question_sources` 均为 0；
  验收 Subject/KnowledgePoint 均删除；旧 Note 仍为 blog=1、mistake=5、note=7。
- 临时管理员最终 `is_admin=false` 且 password hash 为 disabled 哨兵。
- `/manage/page.tsx` diff=0；旧管理登录与业务面板未改。
- 隔离前后端进程已停止；仓库外备份在全部验证通过后删除。

## P0-08 最终审查补充

- 发现合并字段后的题型/options 验证可能直接抛 Pydantic ValidationError；新增回归测试
  先复现失败，再统一转换为 Draft/Question domain validation，避免 HTTP 500。
- 最终后端定向回归：`16 passed`。
- 最终 TSC 与 `git diff --check`：通过。
