# AI 治理：当前 Run 来源与确认契约

日期：2026-10-09。当前源码基线，整体合同 `PARTIAL`。旧文本完整保存在 [历史快照](../audits/archive/AI_GOVERNANCE_PRE_2026-10-09.md)；旧F05 optional source_run_id与NOT_YET_WIRED声明已失效。本文件描述当前实现与缺口，不是实现/迁移/provider/发布授权。

## 当前可达路径

`/manage/capture` 的“从题库记录错题”使用正式 active Question、错误答案与错因，调用 `POST /api/admin/mistakes/ai-candidate`；随后显式 `POST /api/admin/mistakes/ai-confirm` 创建 canonical MistakeDraft。均需后端管理员会话。普通手工创建保留；`MistakeDraftCreate.source_run_id` 非空在 `mistake_service.py:79–87` 被拒绝，不能通过旧 staged run_id 松散绑定。

`admin_mistakes.py:156–180` 在生成时由服务端构造 creation_context（purpose、Question id/version、输入hash、schema/prompt版本）与created_by，传给gateway。生成run成功后返回run_id/review_revision/candidate。正常生成写created_by=admin.id；确认服务的NULL owner兼容不代表所有存量行均有强owner保证。旧行缺canonical creation_context仍会被拒绝，不能由兼容条件直接推断已有越权。失败或无run_id返回错误，不允许当作canonical AI确认成功。

migration034/`models/ai_run.py:52–60`包含created_by、creation_context、confirmed_payload_hash、confirmed_at；旧记录允许NULL读取，不能冒认具备新来源合同。本轮没有执行迁移或历史回填。

## 当前确认实现

`ai_creation_service.py:106–117,143–199`锁定并刷新run，核purpose/task/status/validation/rejection，并在actor_id与created_by均非NULL时拒绝owner不匹配（NULL保留兼容放行）；已绑定且同payload返回原实体，异payload冲突，不再创建；未绑定核expected revision，再由create_entity核live Question id/version并创建draft，同事务保存target/hash/accepted/time。

已绑定重放先于live Question版本校验，题目后改版不应导致同payload重复新建。Capture生成run仍绑定Capture，人工convert不将其伪改绑成Question/Mistake。弃用/拒绝生成可能保持target NULL，不能仅凭NULL认定数据丢失。

## 已确认缺口与禁止过度声明

1. 生成输入hash虽落context，确认没有比对原my_answer/生成错因。UI生成中可改输入，迟到响应没有代次检验；不能称完整来源一致性已验证。
2. confirmed_candidate只入临时hash，Draft写原reason/my_answer等字段；无最终确认快照/edited marker。原output_data是AI原候选，hash不能重建人工确认内容。候选参考/采纳语义需要定版。
3. 通用 `/api/admin/ai/runs/{id}/decision` 在 `ai_run_service.py:277–307` 使用内存revision检查，无同一行锁/CAS；不能声称confirm/reject/accept所有路径已并发安全。
4. gateway起run失败后仍可能调用provider，canonical最终会拒绝无run结果。实体未绕过来源，但外发费用/审计失败合同仍待决定。

以上为源码确证，实际竞争/保存影响未运行复现。详细证据和下阶段退出条件见 [审查A01–A03](../audits/ARCHITECTURE_AUDIT.md)及 [ROADMAP N02](../ROADMAP.md)。

## 调用分类

|调用|实际归类|
|---|---|
|Capture recognition/draft|target-linked到Capture；OCR默认关闭，provider不作本轮验证|
|canonical Mistake AI candidate/confirm|创建型；生成未绑定、显式确认后绑定DraftItem标识；来源/最终确认审计仍PARTIAL|
|legacy staged generation|仍可能返回source_run_id；legacy保存冻结，canonical loose绑定拒绝，不能当已支持保存主线|
|Note polish/summarize/translate等|流式临时预览；未持久采纳时不等于canonical实体创建；并非每次都经Gateway Run|
|diagram、analyze/variant/card/summary/prompt test、recommendation、Netease reason|target覆盖需按当前调用点逐项核验；不能把所有NULL一概豁免或宣称都已绑定|

`backfill_ai_run_target`等低层helper仍存在，不是新canonical确认的受支持入口，不允许以它绕过owner/context/revision。retry复制target不等于重新获准创建另一实体。展示DTO脱敏与重放输入权限须沿现行私有API合同保持。

## 本轮与后续验证

2026-10-09首次架构审查阶段执行前端单测、TS与无DB后端契约；本次文档重新审查未重跑这些测试；没有provider、DB、HTTP保存或浏览器AI流程。后续假provider仅替换外部适配，需真router/service/DB/UI贯通，覆盖来源变更、最终快照、重放/竞争/回滚/写run失败。真实样本外发、费用、生产开关和迁移另需授权。
