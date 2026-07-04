# 任务清单：MVP 本地试运行验收

> 状态：阶段二及临时管理员解阻复跑已完成；最终结论为有条件通过，可进入日常试用观察。全程未修改业务代码。

> 审批记录：用户已于 2026-07-04 明确批准执行阶段 P0-07 至 P0-12，并限定只写本地私有样例数据、无敏感测试附件和验收记录。

## P0-01 建立本地试运行 workflow 入口

- [x] 创建 `README.md`，明确 Batch 0–7 开发关闭、本轮只进入本地试运行验收。
- [x] 明确触及领域、禁止范围和主要文档链接。
- 验证方式：检查 README 是否不包含实现、部署、AI/OCR/BKT/对象存储扩展承诺。

## P0-02 明确本地试运行需求与设计边界

- [x] 创建 `requirements.md`。
- [x] 创建 `design.md`。
- [x] 明确发现问题只记录、不自动修复。
- 验证方式：检查需求和设计是否只覆盖文档/记录，不要求新增代码、脚本或迁移。

## P0-03 准备本地试运行 checklist

- [x] 创建 `checklist.md`。
- [x] 覆盖 subject → knowledge point → question draft → question → mistake draft → mistake → review item → review record → attachment upload/link/read。
- 验证方式：检查 checklist 中每个链路节点都有可勾选项。

## P0-04 准备 sample-data-plan

- [x] 创建 `sample-data-plan.md`。
- [x] 包含 3–5 个 LeetCode 相关练习的人工改写计划和来源标注。
- [x] 明确不得批量抓取、不得 API、不得公开发布。
- 验证方式：检查文档不包含原题全文、爬虫、API 或导入脚本计划。

## P0-05 准备 trial-record 模板

- [x] 创建 `trial-record.md`。
- [x] 能记录环境、样例、对象 ID、链路节点、证据和结论。
- 验证方式：检查模板能区分 pass、partial、fail、blocked、not run。

## P0-06 准备 issues 记录模板

- [x] 创建 `issues.md`。
- [x] 能记录问题严重程度、复现步骤、影响范围、阻塞性和下一步归属。
- 验证方式：检查模板明确问题只记录，不自动修复。

## 阶段二：本地真实试跑（待批准）

### P0-07 建立可复核的本地验收环境

- [x] 记录当前分支、commit、工作树、数据库、前后端地址和管理员认证方式。
- [x] 启动或确认 PostgreSQL、后端和前端可用。
- [x] 验证未登录管理访问被拦截，并确认试跑不依赖 `AUTH_BYPASS`。
- 来源需求：REQ-LT-05、REQ-LT-06。
- 涉及文件：仅本 workflow 的记录文档和 `assets/` 证据；不修改业务代码。
- 完成标准：环境与权限状态均有实际证据，阻塞项已登记。
- 验证方式：服务健康检查、页面检查、日志或既有 API 响应。
- 风险说明：本地环境或认证不可用时停止试跑，不通过改代码绕过。
- 执行结果：环境与未登录保护已验证；管理员 Passkey 因本地 RP ID/Origin 与运行域名不匹配而不可用，登记为 `LT-ISSUE-001`，主链路进入 blocked。

### P0-08 准备 3 条本地私有样例

- [x] 按 `sample-data-plan.md` 准备 two-sum、valid-parentheses、tree-level-order 三条人工转述样例。
- [x] 准备一个无敏感信息的本地文本附件。
- [x] 核对来源标注、私有边界及不复制原题全文。
- 来源需求：REQ-LT-02、REQ-LT-05。
- 涉及文件：本地数据库、附件测试文件、workflow 记录。
- 完成标准：3 条样例和附件符合版权、安全与私有边界。
- 验证方式：人工核对实际录入文本和来源字段。
- 风险说明：不抓取、不接 API、不批量导入。
- 执行结果：3 条转述样例已在 `sample-data-plan.md` 就绪；测试附件为 `assets/LT-20260704-review-note.txt`。因 P0-07 认证阻塞，未写入数据库、未上传。

### P0-09 执行 subject → question 主链路

- [x] 创建并刷新读取 subject 与 knowledge points。
- [x] 为 3 条样例创建 question drafts，并确认为 questions。
- [x] 记录对象 ID、关联、状态转换和页面/API/数据库证据。
- 来源需求：REQ-LT-05。
- 涉及文件：本地数据库和 workflow 记录。
- 完成标准：3 条样例均可从 subject 追溯到正式 question，或失败项有 issue。
- 验证方式：真实页面操作优先，已有管理 API 和数据库查询作为补充证据。
- 风险说明：发现缺少入口或状态转换失败时只记录，不修复。
- 执行结果：临时管理员解阻后复跑通过。subject `135`，knowledge points `21/22/23`；3 个 question draft 均为 201，convert 均为 200，正式 question ID 已记录于 `trial-record.md`。

### P0-10 执行 mistake → review 主链路

- [x] 为 3 条 questions 创建 mistake drafts 并确认为 mistakes。
- [x] 验证 review items 产生并提交至少一次 review record。
- [x] 记录对象 ID、关联、状态变化和页面/API/数据库证据。
- 来源需求：REQ-LT-05。
- 涉及文件：本地数据库和 workflow 记录。
- 完成标准：3 条样例均可追溯至 mistake；至少一条完成 review record，其他项如未运行须说明。
- 验证方式：真实页面操作优先，已有管理 API 和数据库查询作为补充证据。
- 风险说明：复习链路阻塞时停止该链路，不修改业务代码。
- 执行结果：复跑通过。3 个 mistake draft 均为 201、convert 均为 200；3 个 review item 均提交成功，每项可读取 1 条 review record。

### P0-11 执行 attachment upload/link/read

- [x] 上传本地测试附件并读取元数据与内容。
- [x] 将附件关联到一个试跑对象并验证刷新后关联仍存在。
- [x] 记录 attachment/link ID 和页面/API/数据库证据。
- 来源需求：REQ-LT-05。
- 涉及文件：本地数据库、本地上传目录和 workflow 记录。
- 完成标准：upload、link、read 均有实际结果；失败项已登记。
- 验证方式：真实页面或已有管理 API、文件读取及数据库查询。
- 风险说明：不得上传真实私密信息或版权材料，不得公开附件。
- 执行结果：复跑通过。attachment `56eeb372-3db7-43c7-a570-8e72f02f31c8`、link `9367fef4-ea4a-46d0-9ce1-a6471981cf05`；刷新读取均为 200，下载内容 SHA-256 与源文件一致。

### P0-12 复核公开边界并完成试运行报告

- [x] 检查公开 `/blog`、`/notes`、`/mistakes` 和附件访问边界。
- [x] 完成 `checklist.md`、`trial-record.md`、`issues.md`、`validation.md`。
- [x] 将所有未解决项写入 `risks.md`，并在 `next-requirements.md` 转化或明确归档。
- [x] 给出 pass、partial、fail 或 blocked 的最终闭环判断。
- 来源需求：REQ-LT-03、REQ-LT-04、REQ-LT-06。
- 涉及文件：仅本 workflow 文档和 `assets/` 证据。
- 完成标准：所有结论有证据，失败/阻塞/not run 均未被写成通过。
- 验证方式：交叉核对 checklist、trial record、issues、validation、risks 与下一轮需求。
- 风险说明：公开泄露视为 P0 并立即停止。
- 执行结果：解阻复跑后最终结论为有条件通过；公开页面/API 保持可访问且无试跑样例，未登录 DOM 未发现管理员操作入口，私有附件未登录读取为 401。唯一条件项为 `LT-ISSUE-002`。

## 执行阶段审批门

- 阶段二已于 2026-07-04 获得用户明确批准并执行。
- P0-09 至 P0-11 初次因 `LT-ISSUE-001` blocked；临时管理员获批后已全部复跑通过。

## 阶段三：临时管理员解阻复跑

> 审批记录：用户于 2026-07-04 明确允许在代码层设置临时管理员账密并进行测试。

### P0-13 创建受控临时管理员会话

- [x] 使用项目既有 CLI 创建或轮换本地 `temp-admin`。
- [x] 密码仅保存在权限受限的临时文件，并通过密码登录建立本地 cookie 会话。
- [x] 确认 `AUTH_BYPASS` 仍为 false，登录后管理 API 可访问。
- [x] 测试结束后禁用临时管理员并删除临时凭据文件。
- 来源需求：REQ-LT-07。
- 完成标准：认证解阻、无凭据泄露、最终账号禁用。
- 验证方式：登录响应、`/api/auth/me`、管理 API、禁用后登录失败。
- 执行结果：临时账号创建、密码登录和管理 API 均通过；凭据文件为 600 且已删除。账号禁用成功，旧会话变为 403；禁用后密码登录返回 500 而非 401，登记 `LT-ISSUE-002`，不影响账号已失去管理权限的事实。

## 阶段关闭

- [x] MVP 主业务链路、附件链路和公开边界通过真实私有样例验证。
- [x] `LT-ISSUE-001` 降级为非目标环境兼容问题，不进入当前阻塞或专项。
- [x] `LT-ISSUE-002` 保留为有条件通过的唯一条件项，转入 Auth Error Handling Cleanup。
- [x] MVP Rebuild 本轮开发与试运行验收结束，进入日常使用观察。
- [x] 不启动 localhost Passkey、AI、OCR、BKT、完整练习、对象存储或云部署工作。

## 停止条件

- 本轮不修改业务代码。
- 本轮不新增脚本、迁移、导入器、AI/OCR/BKT/云部署相关内容。
- 未获执行阶段批准时，不启动真实试跑或写入样例数据。
