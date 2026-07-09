# 学习系统总流程

> 状态：目标架构，均为拟新增或待迁移能力，不表示代码已经实现。

## 系统定位

本项目由两个边界清晰、共享基础设施的系统组成：

- **公开内容系统**：博客、公开笔记和公开文章展示，只读取 `public + published` 数据。
- **私有学习管理系统**：科目、知识点、题库、练习、错题、复习、附件、OCR、AI、草稿审核、后台任务、搜索、统计和设置，默认私有。

学习系统遵循十项原则：科目是一级学习维度；知识点是题库、错题、复习和 BKT 的核心单位；题目保存题目本体；练习保存作答事实；错题保存错误事实；复习决定复习时机；AI 只生成草稿、建议、报告和分析；草稿审核是正式入库闸门；附件保存原始材料；后台任务处理耗时工作。

## 主数据链路

```text
subjects
  ↓
chapters
  ↓
knowledge_points
  ↓
questions
  ↓
practice_sessions
  ↓
practice_attempts
  ↓
mistakes
  ↓
review_items
  target_type = mistake | knowledge_point | question | note
  target_id = 对应对象 ID
  next_review_at = 第一版当前调度时间
  ↓
review_records
  ↓
knowledge_mastery / knowledge_mastery_events
```

每一层只拥有自己的事实：题目不保存某次作答，练习不拥有复习计划，错题不替代题库，复习不改写题目。

第一版不使用 `review_schedules`。`review_items.target_type/target_id` 定位复习对象，`review_items.next_review_at` 是当前调度时间的唯一权威字段。

链路末端的 `knowledge_mastery`、`knowledge_mastery_events` 与 `bkt_parameters` 是目标能力。第一批只实现 `review_items`、`review_records` 和简单 SM-2；BKT 在数据质量验证后启用。

## 上传识别链路

```text
用户上传文件
  ↓
attachments
  ↓
ocr_jobs / ocr_results / ocr_blocks
  ↓
capture_jobs / capture_results
  ↓
draft_items
  ↓
question_drafts / mistake_drafts / practice_attempt_drafts
  / knowledge_point_suggestions / note_ai_suggestions
  ↓
人工审核确认
  ↓
questions / mistakes / practice_attempts / knowledge_points
```

OCR 只识别文字和版面；Capture Router 判断业务类型；AI、OCR、Capture 必须先创建 `draft_items`，再创建带 `draft_item_id` 的类型化草稿，不能直接写正式表。

## AI 链路

```text
task_type
  ↓
ai_routing_rules
  ↓
ai_model_profiles
  ↓
ai_prompt_templates
  ↓
ai_runs
  ↓
output validator
  ↓
draft_items / reports / suggestions / analysis
```

AI 输出不拥有业务事实。需要进入正式系统的内容必须通过结构校验、规则校验和人工确认。

## 第一版范围

第一版代码范围只覆盖科目/知识点/题库基础、图片与单个 PDF、单文件 OCR/Capture、Question/Mistake 两类草稿审核，以及不依赖 AI 的练习—错题—复习最小闭环。BKT、AI 管理台、jobs、搜索、统计和完整设置保留架构接口，按后续 Phase 与使用证据启用。

## 暂缓范围

向量库、RAG、全自动知识图谱、无确认自动入库、AI 自动修改复习计划或 mastered、多用户分级、大规模批审、音视频解析、压缩包解包、复杂大屏、Elasticsearch/Meilisearch、复杂队列框架、本地大模型和公开题库。

## 兼容旧系统

当前代码仍可能以 `Note(type="mistake")`、`/api/notes`、旧写作页和旧复习页承载部分能力。迁移完成前，这些属于**兼容旧系统**，不能把本文件的目标实体或路由描述成已实现。
