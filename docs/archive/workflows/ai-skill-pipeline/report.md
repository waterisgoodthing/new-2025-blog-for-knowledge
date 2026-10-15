# AI Skill Pipeline Knowledge Base 完备报告

## 1. 报告结论

本报告围绕个人知识系统中的 AI Skill Pipeline Knowledge Base 工作流进行整理与审查，目标是在不提前修改运行时代码的前提下，完成第一阶段知识库能力的规划、设计、验收与交接约束。

综合当前上传内容判断，该工作流已具备进入 `design.md`、`tasks.md` 和 `validation.md` 固化阶段的基础条件。其核心方向正确，范围边界较清晰，能够服务于个人博客、错题集、笔记系统中的考研复习场景。

当前阶段结论如下：

| 项目          | 结论                                      |
| ----------- | --------------------------------------- |
| 工作流定位       | 合格，适合作为 AI 技能管线与知识库一期规划                 |
| 当前状态        | Planning，尚未开始 runtime implementation    |
| 是否允许直接开发    | 不允许，必须等待 `tasks.md` 明确批准                |
| 一期技术路线      | 结构化检索优先，不引入向量数据库                        |
| 知识点建模       | 不创建一等 `KnowledgePoint` 实体               |
| 引用要求        | AI 生成知识内容必须具备 source refs 或 citation 标记 |
| 外部 skill 定位 | 仅作为开发期能力参考，不能作为产品运行时依赖                  |
| 验收重点        | 检索确定性、引用可追溯、字段安全、范围控制                   |

最终建议：

```text
requirements.md
  -> design.md
  -> tasks.md
  -> validation.md
  -> handoff-prompt.md
  -> implementation
  -> validation report
  -> remaining risks
```

在 `tasks.md` 未批准前，任何 runtime 代码、数据库迁移、前端页面、AI Provider 运行时集成都不应开始。

---

## 2. 背景与目标

### 2.1 项目背景

当前个人系统包含博客、笔记、错题、复习等模块。系统已经具备基础内容记录能力，但知识之间的结构化关联、错题复习上下文、弱点归纳、引用支持型文章生成等能力仍处于规划阶段。

本工作流旨在设计一个第一阶段的 AI 技能管线，使现有内容能够形成可检索、可关联、可引用、可生成的个人知识层。

### 2.2 主要目标

本阶段的主要目标是为考研复习场景建立轻量级知识库能力，具体包括：

1. 从现有 `notes`、`mistakes`、`reviews` 中进行结构化检索。
2. 根据学科、知识点、标签、题型、难度、复习状态等字段生成上下文包。
3. 对笔记、错题、复习记录之间的关系进行自动建议。
4. 支持带有 source refs 的 AI 复习总结、弱点报告和知识文章草稿生成。
5. 为后续 social card、NotebookLM、AI provider 管理界面预留扩展空间。
6. 保持 Phase 1 轻量化，避免提前引入向量库、知识图谱或复杂实体建模。

### 2.3 目标使用场景

主要服务场景为考研复习，尤其适合：

* 数学错题归纳
* 数据结构与算法复盘
* 专业课知识点串联
* 周期性弱点总结
* 基于错题与笔记生成复习提纲
* 从已有知识材料生成带引用的博客草稿
* 后续导出错题卡片或复习卡片

---

## 3. 工作流总览

### 3.1 文件定位

本工作流建议放置于：

```text
docs/workflows/ai-skill-pipeline/
```

推荐文件结构：

```text
docs/workflows/ai-skill-pipeline/
  README.md
  requirements.md
  design.md
  tasks.md
  validation.md
  handoff-prompt.md
```

### 3.2 各文件职责

| 文件                  | 职责                                    |
| ------------------- | ------------------------------------- |
| `README.md`         | 工作流总览，说明目标、范围、状态、文件结构                 |
| `requirements.md`   | 定义需求、用户决策、功能需求、非功能需求、一期排除项            |
| `design.md`         | 定义架构、管线、检索、引用、关系建议、API 形态             |
| `tasks.md`          | 定义经过批准的可执行任务                          |
| `validation.md`     | 定义验收计划、验证项、证据格式与验收报告模板                |
| `handoff-prompt.md` | 作为任务批准后交给 Codex/Cursor/OpenClaw 的执行提示 |

### 3.3 阶段门禁

本工作流必须遵循以下阶段顺序：

```text
requirements.md
  -> design.md
  -> tasks.md
  -> validation.md
  -> handoff-prompt.md
  -> implementation
  -> validation report
  -> remaining risks
```

代码实现只能在以下条件同时满足后开始：

1. `tasks.md` 已明确批准。
2. `handoff-prompt.md` 已作为执行提示使用。
3. 执行前已运行 `git status --short`。
4. 已确认不会覆盖用户未提交改动。
5. 已读取 `AGENTS.md` 并遵守其中约束。

---

## 4. 用户决策记录

当前已确认的关键决策如下：

| Decision                              | Value                                                                                                                |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Primary goal                          | Postgraduate exam review                                                                                             |
| First-class `KnowledgePoint` entity   | No, defer until data volume grows                                                                                    |
| Vector database                       | No, defer until after first knowledge-base round                                                                     |
| First retrieval mode                  | Structured retrieval only                                                                                            |
| Automatic bidirectional relations     | Allowed as suggestions                                                                                               |
| Citation requirement                  | Required for AI-generated knowledge output                                                                           |
| Runtime dependency on external skills | No, external skills are development-time capability references unless explicitly integrated through backend services |

这些决策构成 Phase 1 的核心边界。任何实现任务都不得绕过这些约束。

---

## 5. 涉及领域

### 5.1 mistakes

涉及能力：

* 错题 OCR
* 文本分析
* 复习建议
* 相似错题检索
* 错题与笔记关系建议

关键约束：

```text
OCR output must remain faithful extraction.
Humanizer must not run on OCR text, formulas, code, answers, or source references.
```

### 5.2 notes

涉及能力：

* 结构化检索
* 相关笔记召回
* source refs 生成
* 支持知识文章生成

关键约束：

```text
Use existing note fields first.
Do not create first-class KnowledgePoint entities in phase 1.
```

### 5.3 review

涉及能力：

* 弱点统计
* 复习上下文包
* 到期复习优先级
* 错误原因聚合

关键约束：

```text
Weak-point summaries should be based on existing mistake and review data.
```

### 5.4 blog

涉及能力：

* 引用支持型知识文章生成
* 未来博客草稿生成
* 从已有 sources 中生成可审计内容

关键约束：

```text
Blog generation may consume cited sources, but source data remains in the backend knowledge model unless explicitly exported.
```

### 5.5 share

涉及能力：

* 复习卡片
* 错题卡片
* 社交分享卡片
* 文章封面素材

关键约束：

```text
Social export is manual only and should not run automatically on save.
```

### 5.6 manage

涉及未来能力：

* AI provider 设置
* skill pipeline 设置
* 生成安全选项
* 可配置开关

关键约束：

```text
Do not implement manage UI until explicitly approved in tasks.md.
```

---

## 6. AI Skill Pipeline 设计

### 6.1 总体管线

已批准的 pipeline map 如下：

```text
polish:
  - deepseek_polish
  - optional_humanizer

mistake_text_analysis:
  - deepseek_solve
  - tone_refine_for_advice_fields

mistake_ocr:
  - qwen_vl_ocr
  - optional_text_analysis

mistake_social_export:
  - card_generator

knowledge_article:
  - notes_retrieval
  - citation_backed_generation
```

该映射定义能力分配，不代表每个请求都自动执行所有可选步骤。

### 6.2 polish

流程：

```text
deepseek_polish
optional_humanizer
```

用途：

* 改善笔记与博客语言表达。
* 可选降低 AI 化表述。
* 保持原始知识含义。

安全要求：

* 不处理 OCR 文本。
* 不处理公式。
* 不处理代码。
* 不处理答案。
* 不处理 source references。
* 默认不覆盖原始内容。
* 如需完整输出 humanizing，应为 opt-in。

### 6.3 mistake_text_analysis

流程：

```text
deepseek_solve
tone_refine_for_advice_fields
```

用途：

* 生成结构化错题分析。
* 对建议类字段进行语气优化。
* 保留关键题面、答案、知识点与分析逻辑。

字段处理原则：

`deepseek_solve` 阶段可以生成结构化分析字段。

`tone_refine_for_advice_fields` 阶段必须保护：

```text
question
correct_answer
analysis
knowledge_points
```

允许润色：

```text
error_reason
key_step
generalization
review_advice
similar_traps
```

### 6.4 mistake_ocr

流程：

```text
qwen_vl_ocr
optional_text_analysis
```

用途：

* 从图片中提取可见题目内容。
* 在用户明确要求或缺少必要分析数据时，再进行可选分析。

安全要求：

* OCR 是忠实提取，不是改写。
* OCR 输出应与解题分析分开。
* Humanizer 不得处理 OCR 输出。
* 不应默认在 OCR 后自动求解。

### 6.5 mistake_social_export

流程：

```text
card_generator
```

用途：

* 从结构化错题数据生成复习卡片、社交卡片或文章封面素材。

触发方式：

* 错题详情页手动导出。
* 周复习页面手动导出。
* 分享流手动导出。

限制：

```text
Not automatic on save.
Must not mutate original mistake record.
```

### 6.6 knowledge_article

流程：

```text
notes_retrieval
citation_backed_generation
```

用途：

* 生成考研复习总结。
* 生成弱点报告。
* 生成知识文章提纲。
* 生成未来博客草稿。

核心规则：

* 事实性结论尽量绑定 source refs。
* 无引用支撑的内容必须标注为 AI inference。
* 无可用 sources 时，不生成事实性知识文章，应返回 insufficient_context 或待补充提纲。

---

## 7. Phase 1 架构原则

### 7.1 架构范围

Phase 1 是轻量级后端知识层，主要链路为：

```text
notes / mistakes / reviews
  -> structured retrieval
  -> source references
  -> relation suggestions
  -> citation-backed generation contracts
```

### 7.2 不引入内容

Phase 1 不引入：

```text
vector database
embedding model
first-class KnowledgePoint entity
heavy graph modeling
silent relation persistence
full AI provider management UI
NotebookLM runtime integration
```

### 7.3 运行时边界

外部 skills 只能作为开发期能力参考，运行时代码必须通过明确的后端服务和安全契约实现。

允许的运行时抽象包括：

```text
knowledge retrieval service
source reference contract
relation suggestion service
AI provider abstraction
AI pipeline orchestration
citation-backed generation service
```

不允许的方式包括：

```text
runtime dependency on ~/.openclaw/skills
runtime dependency on ~/.claude/skills
hidden Codex skill invocation
hidden OpenClaw skill invocation
hidden Claude Code skill invocation
```

---

## 8. 结构化检索设计

### 8.1 建议服务位置

建议新增或规划服务：

```text
backend/app/services/knowledge_retrieval.py
```

### 8.2 输入字段

结构化检索应优先使用现有字段：

```text
subject
knowledge_points
tags
type
difficulty
ai_metadata
created_at
updated_at
last_reviewed / last_reviewed_at
next_review / next_review_at
review state
limit
```

实现前必须先检查现有模型与迁移文件，确认真实字段名。

### 8.3 匹配策略

Phase 1 检索策略以结构化规则为主：

1. 学科精确或规范化匹配。
2. `knowledge_points` 按逗号、顿号、分号等分隔后匹配。
3. 标签重叠匹配。
4. 类型匹配。
5. 难度匹配。
6. 最近错题加权。
7. 到期复习加权。
8. 同学科且知识点重叠的笔记作为解释候选。
9. 同学科且错误原因相近的错题作为相似错题候选。

### 8.4 建议评分模型

Phase 1 可采用简单可解释评分：

```text
score =
  subject_match * 3
+ knowledge_point_overlap * 4
+ tag_overlap * 2
+ type_match * 1
+ due_review_bonus * 2
+ recent_mistake_bonus * 2
- stale_penalty
```

该评分可先作为服务内部逻辑，不需要持久化。

---

## 9. Source Reference Contract

### 9.1 笔记 source ref

建议结构：

```json
{
  "source_type": "note",
  "source_id": "abc",
  "title": "条件概率笔记",
  "slug": "conditional-probability",
  "field": "content",
  "excerpt": "贝叶斯公式用于已知结果反推原因概率...",
  "url": "/notes/conditional-probability",
  "confidence": 0.86,
  "match_reasons": ["subject_match", "knowledge_point_overlap"]
}
```

### 9.2 错题 source ref

建议结构：

```json
{
  "source_type": "mistake",
  "source_id": "123",
  "title": "条件概率错题",
  "field": "analysis",
  "excerpt": "本题错误来自混淆 P(A|B) 与 P(B|A)...",
  "url": "/notes/conditional-probability-mistake",
  "confidence": 0.82,
  "match_reasons": ["subject_match", "error_reason_match"]
}
```

### 9.3 引用原则

Source ref 必须满足：

1. 能追溯到已有 note、mistake 或 review。
2. 包含 source type。
3. 包含 source ID。
4. 包含字段名。
5. 尽量包含 excerpt。
6. 不允许 AI 生成不存在的 source ID。
7. 不允许对 source excerpt 进行 humanizer 改写。

---

## 10. Relation Suggestion Contract

### 10.1 关系类型

初始 relation types：

| 类型             | 含义             |
| -------------- | -------------- |
| `explains`     | 一篇笔记解释一道错题     |
| `similar`      | 两道错题相似         |
| `prerequisite` | 一个来源提供前置知识     |
| `follow_up`    | 一个来源适合后续复习     |
| `source_for`   | 一个来源可支撑生成总结或文章 |

### 10.2 建议结构

```json
{
  "source_type": "mistake",
  "source_id": "123",
  "target_type": "note",
  "target_id": "abc",
  "relation_type": "explains",
  "score": 0.82,
  "reason": "同属数学，知识点均包含条件概率、贝叶斯公式",
  "status": "suggested"
}
```

### 10.3 Phase 1 限制

Phase 1 中 relation 只作为建议返回，不应静默持久化为已确认事实。

不允许：

```text
silent confirmation
silent persistence
automatic pin
automatic ignore
automatic graph mutation
```

后续阶段可考虑加入：

```text
confirm
ignore
pin
relation persistence
relation graph view
```

---

## 11. API 设计建议

### 11.1 `POST /api/knowledge/context-pack`

用途：

```text
只做检索、统计、关系建议，不调用生成模型。
```

请求示例：

```json
{
  "subject": "数学",
  "knowledge_points": ["条件概率", "贝叶斯公式"],
  "tags": ["概率论", "错题"],
  "type": "mistake",
  "difficulty": "medium",
  "date_range": {
    "from": "2026-05-01",
    "to": "2026-06-05"
  },
  "review_state": "due",
  "limit": 10
}
```

响应结构：

```json
{
  "sources": [],
  "related_notes": [],
  "related_mistakes": [],
  "suggested_relations": [],
  "stats": {
    "mistake_count": 0,
    "note_count": 0,
    "top_error_reasons": []
  }
}
```

硬性约束：

```text
This endpoint must not call DeepSeek, Qwen, OpenAI, OpenClaw skills, Claude Code skills, or any external AI provider.
```

### 11.2 `GET /api/knowledge/weak-points?days=30`

用途：

```text
基于最近错题、复习状态、错误原因统计薄弱点。
```

响应示例：

```json
{
  "days": 30,
  "weak_points": [
    {
      "subject": "数学",
      "knowledge_point": "条件概率",
      "mistake_count": 5,
      "due_review_count": 2,
      "recent_error_count": 3,
      "top_error_reasons": ["混淆条件方向", "审题不完整"],
      "evidence_sources": []
    }
  ]
}
```

硬性约束：

```text
This endpoint must be deterministic and must not call external AI providers.
```

### 11.3 `POST /api/ai/knowledge-summary`

用途：

```text
基于 context-pack 的 sources 生成总结、复习报告、博客草稿。
```

请求示例：

```json
{
  "mode": "exam_review_summary",
  "context_pack": {
    "sources": [],
    "related_notes": [],
    "related_mistakes": [],
    "suggested_relations": [],
    "stats": {}
  },
  "requirements": {
    "language": "zh-CN",
    "style": "exam_review",
    "max_length": 1200,
    "require_citations": true
  }
}
```

响应建议：

```json
{
  "title": "条件概率薄弱点总结",
  "blocks": [
    {
      "type": "source_backed_claim",
      "text": "你在条件概率题目中主要错误是混淆 P(A|B) 与 P(B|A)。",
      "source_refs": [
        {
          "source_type": "mistake",
          "source_id": "123",
          "field": "analysis"
        }
      ]
    },
    {
      "type": "ai_inference",
      "text": "后续复习应优先训练条件方向识别。",
      "source_refs": []
    }
  ]
}
```

如果 sources 不足，应返回：

```json
{
  "status": "insufficient_context",
  "message": "No usable source references are available for factual generation.",
  "outline": []
}
```

---

## 12. 外部 Skill 安装与定位

### 12.1 Skill 列表

计划记录以下开发期 skill：

```bash
cd ~/.openclaw/skills

# Or Claude Code:
# cd ~/.claude/skills

git clone https://github.com/op7418/Humanizer-zh.git
git clone https://github.com/op7418/guizang-social-card-skill.git
git clone https://github.com/helloianneo/ian-xiaohei-illustrations.git
git clone https://github.com/PleasePrompto/notebooklm-skill.git
```

### 12.2 安装注意事项

#### ian-xiaohei-illustrations

如果 `SKILL.md` 位于嵌套目录，需要移动到 skill root：

```bash
cd ian-xiaohei-illustrations
mv ian-xiaohei-illustrations/* . && rmdir ian-xiaohei-illustrations
```

#### notebooklm-skill

首次使用可能安装：

```text
Python virtual environment
Chromium browser
```

需要网络可用。

#### notebooklm-mcp

本工作流目标是：

```text
notebooklm-skill
```

不是：

```text
notebooklm-mcp
```

### 12.3 运行时边界

这些 skill 只能作为开发期能力参考。

运行时代码不得依赖：

```text
~/.openclaw/skills
~/.claude/skills
local skill folders
hidden skill invocations
```

产品运行时必须调用明确的 backend services 或 provider abstraction。

---

## 13. 非功能需求

| 类型            | 要求                                                            |
| ------------- | ------------------------------------------------------------- |
| Accuracy      | Review 与 OCR 流程优先保证正确性，不追求自然风格                                |
| Safety        | API keys 不得暴露到前端                                              |
| Performance   | optional skill steps 不得默认拖慢每次 AI 调用                           |
| Extensibility | 管线设计应支持未来 AI 配置管理                                             |
| Traceability  | citation-backed output 必须能从 source refs 审计                    |
| Scope control | Phase 1 避免向量搜索与重型图建模                                          |
| Determinism   | retrieval 与 weak-point endpoints 不得调用外部 AI                    |
| Auditability  | source-backed block 应能追溯到 source type、source ID、field、excerpt |

---

## 14. Phase 1 排除项

Phase 1 明确排除：

```text
Vector database setup.
Embedding model selection.
First-class KnowledgePoint database table.
NotebookLM runtime integration.
Silent automatic relation persistence.
Full AI provider management UI.
Production-grade API key encryption design.
Frontend implementation before task approval.
Runtime dependency on OpenClaw or Claude Code skills.
Automatic AI calls inside deterministic retrieval endpoints.
Silent overwrite of original note, mistake, OCR, formula, code, answer, or source-reference content.
```

---

## 15. 验收计划

### 15.1 当前验证状态

当前状态：

```text
No runtime validation has been performed yet.
This workflow is currently in planning.
```

runtime validation 不得在以下条件满足前开始：

```text
tasks.md is explicitly approved
implementation tasks are executed
handoff-prompt.md is used for controlled execution
```

### 15.2 验收原则

Phase 1 验收必须验证：

```text
structured retrieval
source references
relation suggestions
citation-backed generation
pipeline safety
scope control
```

不得通过以下实现：

```text
vector database
embedding retrieval
first-class KnowledgePoint entity
silent relation persistence
unapproved frontend implementation
runtime dependency on OpenClaw or Claude Code skills
AI calls inside deterministic retrieval endpoints
```

### 15.3 证据要求

每个任务完成后必须记录：

| Evidence Type       | Required Content                                  |
| ------------------- | ------------------------------------------------- |
| Changed files       | 改动文件列表                                            |
| Test command        | 实际运行的测试命令                                         |
| Test result         | pass / fail / skipped / blocked                   |
| Manual verification | curl、API response sample、screenshot 或 log excerpt |
| Risk notes          | 剩余风险                                              |
| Scope check         | 确认未加入越界功能                                         |

禁止无证据标记任务完成。

### 15.4 核心验收项

#### V1 Planning Gate

检查文件是否存在：

```text
requirements.md
design.md
tasks.md
validation.md
handoff-prompt.md
```

#### V2 Scope Control

检查是否未引入：

```text
vector database
embedding model
first-class KnowledgePoint table/model
silent persistent relation graph
frontend routes or pages unless explicitly approved
runtime dependency on OpenClaw or Claude Code skills
```

#### V3 Existing Model Mapping

实现前必须检查：

```text
notes
mistakes
reviews
existing AI metadata fields
existing review timestamp fields
```

#### V4 Structured Retrieval

目标接口：

```text
POST /api/knowledge/context-pack
```

验收重点：

```text
subject matching works
knowledge_points matching works
tags matching works if tags exist
date range filtering works if provided
limit is respected
empty result is handled safely
no external AI call
```

#### V5 Weak-Point Summary

目标接口：

```text
GET /api/knowledge/weak-points?days=30
```

验收重点：

```text
days parameter is respected
recent mistakes are counted
due reviews are counted if review fields exist
top error reasons are returned when available
empty dataset returns a safe empty response
no external AI call
```

#### V6 Source Reference Contract

source refs 至少应包含：

```text
source_type
source_id
title
field
excerpt
url if available
confidence or score if available
match_reasons if available
```

#### V7 Relation Suggestion

relation suggestions 至少应包含：

```text
source_type
source_id
target_type
target_id
relation_type
score
reason
status
```

默认状态：

```text
suggested
```

#### V8 Citation-Backed Generation

生成输出必须区分：

```text
source_backed_claim
ai_inference
insufficient_context
```

必须验证：

```text
source-backed claims include source refs
AI-only synthesis is labeled as AI inference
missing source coverage is reported
no invented source IDs appear
empty sources do not produce unsupported factual articles
```

#### V9 Field Safety

保护内容包括：

```text
question
correct_answer
formulas
code
OCR text
raw OCR output
JSON keys
source identifiers
source excerpts
URLs
slugs
IDs
original user answers
analysis during tone refinement
knowledge_points during tone refinement
```

#### V10 OCR Safety

验证：

```text
OCR output is stored or returned separately from solved analysis
humanizer does not run on OCR output
optional_text_analysis runs only when explicitly requested or required by missing data
```

#### V11 Social Card Export

验证：

```text
saving a mistake does not trigger card generation
export reads structured mistake data
export does not modify the original mistake record
```

#### V12 Security

验证：

```text
API keys are not exposed to frontend code
provider secrets are read from backend environment/config only
runtime code does not depend on local skill folders
logs do not print API keys or full provider secrets
```

#### V13 Performance

验证：

```text
optional_humanizer does not run by default on every AI call
social card export is manual
deterministic retrieval endpoints do not call external AI
context-pack respects limit
```

---

## 16. Handoff Prompt 执行约束

任务批准后，交给 Codex/Cursor/OpenClaw 的执行提示必须强调：

1. 项目路径：

```text
/Users/limengyang/2025-blog-public
```

2. 必须严格遵守：

```text
AGENTS.md
```

3. 必须先读取：

```text
AGENTS.md
docs/workflows/ai-skill-pipeline/design.md
docs/workflows/ai-skill-pipeline/tasks.md
```

4. 改代码前必须运行：

```bash
git status --short
```

5. 必须保护用户改动。

6. 每完成一个任务，必须立即更新 `tasks.md`：

```text
status
changed files
tests run
manual verification command if applicable
remaining risks
```

7. 必须禁止：

```text
vector database
first-class KnowledgePoint entity
unapproved schema migrations
frontend routes or frontend pages
runtime dependency on OpenClaw or Claude Code skills
AI calls inside deterministic retrieval endpoints
silent overwrite of protected fields
```

8. 遇到以下情况必须停止并报告：

```text
AGENTS.md conflicts with the task
required existing models cannot be found
a task requires schema changes but no migration is approved
an implementation would require frontend work not approved in tasks.md
external AI provider configuration is missing
tests fail for reasons outside the current task scope
```

---

## 17. 建议任务拆分

建议后续 `tasks.md` 至少包含以下任务：

| 编号    | 优先级 | 任务                                    | 说明                             |
| ----- | --- | ------------------------------------- | ------------------------------ |
| T-001 | P0  | 梳理现有 Notes / Mistakes / Reviews 模型字段  | 防止乱建表与错用字段                     |
| T-002 | P0  | 定义 source ref schema                  | 为引用生成提供统一结构                    |
| T-003 | P0  | 定义 relation suggestion schema         | 关系只作为 suggested 返回             |
| T-004 | P0  | 实现或规划 `knowledge_retrieval.py`        | 结构化检索核心                        |
| T-005 | P0  | 实现 `POST /api/knowledge/context-pack` | 只做检索，不调用 AI                    |
| T-006 | P1  | 实现 `GET /api/knowledge/weak-points`   | 统计薄弱点                          |
| T-007 | P1  | 实现 `POST /api/ai/knowledge-summary`   | 基于 sources 生成引用型总结             |
| T-008 | P1  | 加入 field safety 规则                    | 限制 humanizer 与 tone refinement |
| T-009 | P1  | 加入 OCR safety 规则                      | OCR 与分析分离                      |
| T-010 | P2  | 规划 social card export                 | 仅手动导出                          |
| T-011 | P2  | 编写 validation report 模板               | 固化验收证据链                        |

其中 P0 任务完成前，不应进入前端或高级 AI provider 管理。

---

## 18. 主要风险与控制措施

### 18.1 范围膨胀风险

风险：

```text
提前引入向量库、知识图谱、KnowledgePoint 表、前端管理页。
```

控制：

```text
Phase 1 明确只做 structured retrieval + source refs + relation suggestions + citation-backed generation contract。
```

### 18.2 AI 生成幻觉风险

风险：

```text
AI 生成复习总结时编造引用、隐藏资料不足、生成无来源事实。
```

控制：

```text
输出必须区分 source_backed_claim、ai_inference、insufficient_context。
无 sources 时禁止生成事实性文章。
```

### 18.3 OCR 污染风险

风险：

```text
OCR 输出被 humanizer 或 polish 改写，导致题面失真。
```

控制：

```text
OCR text / raw OCR output 为保护字段，不允许改写。
OCR 与 solved analysis 分离。
```

### 18.4 原始内容被覆盖风险

风险：

```text
polish 或 humanizer 覆盖原始笔记、错题、答案、公式、代码。
```

控制：

```text
默认生成临时结果或独立字段。
未经明确确认不得覆盖原文。
```

### 18.5 外部 skill 运行时依赖风险

风险：

```text
产品运行依赖 ~/.openclaw/skills 或 ~/.claude/skills。
```

控制：

```text
skill 仅作为开发期能力参考。
runtime 必须调用明确 backend services 或 provider abstraction。
```

### 18.6 验收证据不足风险

风险：

```text
AI 执行器声称完成，但没有测试、curl、日志、diff 证据。
```

控制：

```text
每个任务完成后必须更新 tasks.md，记录 changed files、tests run、manual verification、remaining risks。
```

---

## 19. 最终判定

当前上传内容已经形成较完整的 AI Skill Pipeline Knowledge Base 工作流基础。

各文件成熟度判断如下：

| 文件                | 当前成熟度     | 结论                 |
| ----------------- | --------- | ------------------ |
| README / 总览       | 较完整       | 可作为工作流入口           |
| requirements.md   | 基本合格      | 小修后可锁定             |
| design.md         | 方向正确      | 需补模型映射、API 契约、评分规则 |
| validation.md     | 原始内容过薄    | 应扩展为验收计划与报告模板      |
| handoff-prompt.md | 方向正确      | 需强化禁止项、证据要求、停止条件   |
| tasks.md          | 待生成 / 待批准 | 未批准前不得实现           |

总体结论：

```text
该工作流可以进入正式文档固化阶段。
当前不应开始 runtime implementation。
下一步应完成 design.md 最终修订、tasks.md 拆分、validation.md 固化、handoff-prompt.md 锁定。
```

---

## 20. 建议下一步

建议按以下顺序执行：

```text
1. 固化 README.md
2. 固化 requirements.md
3. 修订 design.md，补充现有模型映射、API 契约、评分规则
4. 生成 tasks.md，但先不批准执行
5. 固化 validation.md
6. 固化 handoff-prompt.md
7. 审查 tasks.md 是否越界
8. 批准 P0 tasks
9. 交给 Codex/Cursor 执行
10. 根据 validation.md 生成验收报告
11. 汇总 remaining-risks.md
12. 决定是否进入前端入口或 Phase 2
```

当前最优先补齐的是：

```text
Existing Model Mapping
API Request / Response Contract
Retrieval Scoring Rule
Citation Output Block Contract
Task Evidence Format
```

完成这些后，该工作流就能形成比较稳固的“需求 → 设计 → 任务 → 验收 → 交接 → 风险回流”闭环。
