# 统一大方案任务清单

> 当前状态：I0–I9 已完成并通过；I10 技术 dry-run PASS 但 `DRY_RUN_READY` 因 owner/backfill 责任未收敛而 BLOCKED；I11 单独批准已收到，但 E-05/E-06 仍受 owner gate 阻断。不得扩大为源库/生产迁移、部署、权威切换、旧系统停写或真实 AI 成功调用。

## I3：Attempt、错题转换与采集手工回退（已完成）

> 本增量将修改后端模型、schema、API、前端私有管理页并新增 Alembic migration。只有明确批准 I3-01 至 I3-10 后才能开始；批准不授权迁移到源库/生产、部署、权威切换、旧系统停写、真实 AI 调用或公开 Attempt 数据。

- [x] I3-01 已新增 Attempt 服务测试：错误 Attempt 只创建一个 pending Mistake Draft、正确 Attempt 不创建 Draft；Capture 既有手工/失败测试一并通过。
- [x] I3-02 已新增 Attempt model/schema/service/admin router 与 Alembic `021`；隔离库 `020 → 021 → 020 → 021` 验证通过。
- [x] I3-03 已扩展 Mistake Draft 来源约束与服务；错误 Attempt 幂等创建 pending Draft，正确 Attempt 不创建 Draft，且不直接创建 Mistake/Review Item。
- [x] I3-04 已在题目详情实现管理员作答与错误反馈，错误作答跳转既有 Mistake Draft 审核，不绕过人工确认。
- [x] I3-05 已启用既有 Capture 工作区；保留上传、识别、草稿和转换状态，并暴露既有手工题目/错题入口作为 AI/OCR 不可用时的回退。
- [x] I3-06 已验证匿名 `POST /api/admin/attempts` 为 401；管理员浏览器成功提交；同一 Attempt 的 Draft 生成保持幂等（定向测试）。
- [x] I3-07 已在 I1 备份恢复的独立数据库执行 `020 → 021 → 020 → 021`、`alembic check`、14 项后端定向测试和 TypeScript 检查。
- [x] I3-08 已在独立生产构建浏览器完成完整最小闭环；C-01/C-02/C-03 已更新为隔离验证通过。
- [x] I3-09 已完成代码质量审查：路由薄、管理员依赖显式、迁移/模型一致；保留答案等值判定与单管理员边界的已知范围限制。
- [x] I3-10 已停止临时后端、生产前端、PostgreSQL 与自动化浏览器；恢复数据库/附件目录和临时前端副本已移入系统废纸篓，并完成记录更新。

## I4：学习首页状态与统一导航收口（已完成）

> 本增量只解决 C-04、C-05：学习首页的加载/局部失败/空态/权限表达，以及学习工作区导航、旧入口兼容和移动端导航。批准 I4-01 至 I4-09 后才可修改源码；批准不授权资料偏好、OCR、文件工作区、源库/生产迁移、部署或公开私有学习数据。

- [x] I4-01 已补充 Dashboard 不可用状态与 Capture 导航事实测试；覆盖局部不可用时仍保留安全行动入口。
- [x] I4-02 已扩展 Dashboard summary 为学习/活动区块状态，并在数据库查询错误时返回安全的 unavailable 摘要，不再误报数据库正常。
- [x] I4-03 已验证局部不可用/空态保留安全行动入口；匿名和失效会话回到既有登录入口，不展示私有摘要。
- [x] I4-04 已将 Capture 导航状态校正为 active；AI、任务、搜索、分析仍保留明确的后续标识。
- [x] I4-05 已完成旧入口决策：`/manage` 保留为受保护登录入口，`/manage/dashboard` 为规范工作区入口；现有公开页均指向规范入口，不新增重定向或第二套导航。
- [x] I4-06 已核验桌面/移动导航共用 `navGroups`；移动抽屉已有当前路由、高亮、焦点陷阱、Escape、背景隔离和可访问名称，定向测试通过。
- [x] I4-07 已通过 Dashboard/导航定向测试、TypeScript、生产构建、Python 编译与隔离 revision `021` 的 Dashboard 后端测试。
- [x] I4-08 已在独立生产构建完成匿名/管理员、空态/失败态、390×844、1280×800、1440×900 与移动键盘导航验证。
- [x] I4-09 已记录代码质量与风险；临时后端、前端和浏览器已停止并清理，用户指定的测试数据库目标保留运行。

## I2-R：管理端认证加载阻塞修复（待批准）

> 此小节扩展为前端源代码修复，必须获得用户对本节任务清单的明确批准后才能执行。批准不授权迁移、部署、生产数据写入、AUTH_BYPASS 或 I2-R 以外的重构。

- [x] I2R-01 根因调查完成：复现由并行开发服务共用 `.next` 输出目录造成，非 `useAdminAuth` / `AuthGate` 源码行为。
- [x] I2R-02 跳过源码修复：根因不在认证代码；保持共享 hook、gate、公开页面和后端权限边界不变。
- [x] I2R-03 已以独立 Git worktree / `.next` 输出目录的生产构建重建隔离环境；匿名 401 显示登录表单，密码管理员会话可进入工作区，独立构建 TypeScript 阶段通过。
- [x] I2R-04 已在独立隔离环境重试 C-01 至 C-03，并即时记录结果。

> 执行顺序、每次增量的范围和停止条件见 [递进执行计划](./incremental-plan.md)。一次只批准并执行一个增量；下一个增量必须等待前一增量的验收记录与新的用户批准。

## A. 方案合并与冻结

- [x] A-01 审阅并批准统一主方案的产品定位、导航和领域边界。I0-DEC-01 已于 2026-07-20 获用户批准。
- [x] A-02 审阅并批准 MVP 与长期愿景拆分。I0-DEC-02 已于 2026-07-20 获用户批准。
- [x] A-03 审阅并批准 Phase 0–8 阶段顺序、停止条件和不做事项。I0-DEC-03 已于 2026-07-20 获用户批准。
- [x] A-04 将已批准的统一方案与既有 V2 文档建立唯一引用关系。见 [I0 冻结审查与来源索引](./i0-freeze-audit.md)。
- [x] A-05 为旧方案、历史审计与当前实现建立“目标/历史/现状证据”索引，并注明事实截至日期与替代关系。见 [I0 冻结审查与来源索引](./i0-freeze-audit.md)。

## B. Phase 0：边界与恢复门槛

- [x] B-01 建立公开/管理员/私有/治理权限矩阵，并列出匿名、管理员、失效会话和不可见资源的预期结果。见 [I1 边界与恢复审计](./i1-boundary-recovery-audit.md)。
- [x] B-02 冻结 content、knowledge、question、mistake、review、attachment、workspace node 的所有权与稳定 ID 规则。见 [I1 边界与恢复审计](./i1-boundary-recovery-audit.md)。
- [x] B-03 建立当前 API/页面/旧写入口/导出方向矩阵，明确 `/api/notes` 与目标 `/api/public/**` 的兼容与退役条件。见 [I1 边界与恢复审计](./i1-boundary-recovery-audit.md)。
- [x] B-04 取得当前 revision 的数据库与附件备份可读性证据。2026-07-20 已在仓库外生成数据库 dump、附件快照和 SHA-256 清单，并验证 dump 可读。见 [I1 边界与恢复审计](./i1-boundary-recovery-audit.md)。
- [x] B-05 在隔离环境验证当前 revision 的数据库与附件联合恢复，并记录结果。2026-07-20 已恢复 revision 020 并核对关键计数和附件哈希；临时恢复目录已移入系统废纸篓。见 [I1 边界与恢复审计](./i1-boundary-recovery-audit.md)。
- [x] B-06 审计 Alembic/model/schema authority 及启动行为，形成修复方案；未经批准不得改 schema。见 [I1 边界与恢复审计](./i1-boundary-recovery-audit.md)。

## C. Phase 1–2：最小闭环与产品化

- [x] C-01 已在 I3 独立生产构建中完成 Question → Attempt；管理员错误作答生成待确认 Mistake Draft，匿名写入为 401。
- [x] C-02 已在 I3 独立生产构建中完成 Attempt → Mistake Draft → Mistake → Review Item → Review Record；仅 Draft 确认后创建正式 Mistake/Review Item。
- [x] C-03 已在 I3 独立生产构建中触发无可用 AI provider 的识别失败，并切换至手工录题，成功进入 Question Draft 审核；未执行真实 AI 成功调用。
- [x] C-04 已完成今日摘要局部失败、空态和权限状态收口。
- [x] C-05 已冻结统一主导航、旧入口兼容和移动端导航。

## I4 closure-fix：收口补丁（已完成，不进入 I5）

> 这是 I4 的小型 closure-fix，不是 I5 的预实施。CF-01 至 CF-06 已获批准并完成；批准不授权迁移、部署、源库写入、真实 AI 调用或 I5 的资料/偏好能力。

- [x] CF-01 将 Dashboard learning、activity、storage 改为独立查询结果，分别支持 ready、unavailable/unknown 与明确 empty；补齐前后端契约和测试 fixture。已由 Dashboard 服务、schema、客户端类型及 7 项 overview 测试覆盖。
- [x] CF-02 在 Dashboard SQL 异常降级前显式 `rollback()`，确保依赖收尾不会 commit 失败事务；保留安全 unavailable 响应。路由与服务异常分支均已 rollback。
- [x] CF-03 增加真实 `get_db` dependency 生命周期测试，验证异常后的 rollback、正常 commit、close，以及同一生命周期的后续查询可恢复。真实生命周期测试 2 项通过。
- [x] CF-04 补测 learning unavailable、activity unavailable、storage unknown、匿名 401、失效会话和 Dashboard retry；不以 mock 依赖存在性替代行为测试。前端定向测试 17 项、后端定向测试 4 项通过；匿名与失效会话均返回 401。
- [x] CF-05 在 `assets/i4-closure-fix/` 保存 390×844、1280×800、1440×900 和键盘导航截图/记录，并从 `validation.md` 逐项链接。资产已归档并逐项链接。
- [x] CF-06 补齐残余风险、I4 归档/保留决定，统一 README、tasks、validation、incremental-plan；仅 closure-fix 全部通过后将 I4 标为 `COMPLETE / PASS`。已完成统一，I4 标记 `COMPLETE / PASS`，I5 随后单独审批并已完成。

## I5：私有资料、首页偏好与响应式验收（已完成）

> 用户已批准 I5-01 至 I5-10，且全部完成并通过。详细范围、边界和证据见 [I5 准备设计](./i5-preparation-design.md)、[I5 准备需求](./i5-preparation-requirements.md)、[I5 准备任务清单](./i5-preparation-tasks.md) 与 [validation](./validation.md)。本轮只在隔离测试目标执行 migration 验证，不涉及源库、生产数据、部署或权威切换。

- [x] I5-01～I5-10 已按 [I5 准备任务清单](./i5-preparation-tasks.md) 执行，全部 `COMPLETE / PASS`。
- [x] C-06 已将欢迎语、资料、品牌边界、时区和首页偏好接入受保护设置；公开 `site-settings` 契约保持独立。
- [x] C-07 已完成桌面、移动端、公开页面和管理员页面验收，资产已链接至 [validation](./validation.md)。

## I6：采集到草稿的深化链路（已完成）

> I6-01 至 I6-08 已获用户批准并完成。详细实现、测试和浏览器证据见 [I6 workflow](../i6-capture-draft-chain/README.md)。本增量未执行源库/生产迁移、部署、推送或真实 AI 成功调用。

- [x] I6-01～I6-08 已完成：022 后端定向组合 51 项、前端定向 33 项、TypeScript、生产构建、Python compileall、diff check 和三尺寸浏览器证据通过。
- [x] D-01 已完成最小私有单文件上传、Capture 状态机、单图识别安全失败和人工回退。
- [x] D-02 已完成 Capture → Question/Mistake Draft 的人工确认闸门、拒绝、修正、版本冲突、幂等转换和来源链测试。

## D. Phase 4–6：知识工作区与治理

- [x] D-01 建立采集、私有附件上传和单文件 OCR 的最小链路（已由 I6 完成）
- [x] D-02 建立 Draft Item 的确认、拒绝、修正、幂等转换与审计链路（已由 I6 完成）
- [x] D-03 设计并验收文件节点、资源引用、上传状态机和发布关系（I7 PASS；隔离 023、API/DB/浏览器证据）
- [x] D-04 实现文件夹树与私有附件预览（I7 PASS；管理员/匿名/失效三尺寸浏览器证据）
- [x] D-05 实现移动、重命名、回收站、恢复、冲突处理与审计（I7 PASS；服务组合测试与审计断言）
- [x] D-06 实现 Markdown 编辑/预览与版本历史（I8 PASS；revision 024、API/DB/浏览器证据）
- [x] D-07 实现 WikiLink、反向链接和属性，验证移动后链接稳定（I8 PASS；稳定 note ID 反链与浏览器/服务证据）
- [x] D-08 实现 PostgreSQL 全文/trigram 搜索与权限过滤（I8 PASS；隔离 pg_trgm、管理员搜索和匿名负向浏览器证据）
- [x] D-09 按真实使用证据分别补齐 AI、任务、统计、报告和设置页面（I9 PASS；真实来源治理 API、空/失败/未提供态、管理员/匿名/失效三尺寸浏览器证据）

## E. Phase 7–8：迁移与归档

- [x] E-01 完成旧系统只读盘点、哈希清单和来源基线（PASS；`blog_db:5432` revision 020、静态索引与 manifest）
- [x] E-02 冻结字段映射、重复判定、冲突处理和 legacy route alias（PARTIAL；技术映射通过，owner/backfill 责任 UNKNOWN）
- [x] E-03 判定 `DRY_RUN_READY` 门槛（BLOCKED；旧实体缺统一 owner，未通过则停止）
- [x] E-04 在隔离目标执行 dry-run，核对计数、哈希、关系和回滚销毁结果（TECHNICAL PASS；020→024→020→024，独立对账后销毁）
- [ ] E-05 经单独批准后执行影子迁移和增量对账（批准已收到；owner/backfill gate BLOCKED）
- [ ] E-06 经单独批准后执行权威切换、观察期和旧系统只读归档（批准已收到；依赖 E-05 与 owner gate）

## F. 最终收口

- [ ] F-01 完成端到端连接性、恢复、权限、浏览器和代码质量审查
- [ ] F-02 完成部署资格审查；失败门槛必须阻断发布
- [ ] F-03 形成最终完成报告，分别声明 MVP、产品化、生产发布和迁移状态
