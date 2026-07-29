# 题库系统设计

## 1. 系统定位

题库系统保存题目本体，是练习、错题和未来复习能力共享的基础数据层。题库系统不等于错题系统；做对和做错的题都可以进入题库。

## 2. 系统职责

- 保存题干、题型、学科、难度、知识点、状态和可见性。
- 维护试卷、书籍、图片、PDF、手工输入和外部链接等来源。
- 提供稳定 Question ID，支持练习、错题和复习引用。
- 通过规范化文本与 hash 提供去重候选，保留合并审计。

## 3. 不负责的内容

- 不记录某次作答、正确与否或练习报告。
- 不维护错题特有的错因和复盘状态。
- 不安排复习，不直接调用 AI，不根据 AI 相似度静默合并。

## 4. 核心实体

- `questions`：题目本体。
- `question_sources`：题目来源。
- Taxonomy 关系：Subject、Knowledge Point 与 Tag。
- Attachment 关系：题图、答案图或来源文件。

`questions` 第一版字段建议：`id`、`subject_id`、`title`、`question_text`、`question_type`、`options`、`correct_answer`、`explanation`、`difficulty`、`learning_level`、`answer_status`、`visibility`、`status` 和时间戳。

`question_sources` 保存 `question_id`、`source_type`、`source_name`、`source_ref`、`external_url`、`source_location`、`attachment_id`、`page_index`、`ocr_block_id` 和时间戳。`source_location` 是 JSON，可记录 `bbox`、`page_range`、`block_range` 等区域信息，使题目能追溯原附件、页码、OCR block 和具体版面区域。题目与知识点只通过 `knowledge_point_links.target_type/target_id` 连接；知识点之间的关系使用 `knowledge_relations`。

## 5. 与练习系统的关系

Practice Attempt 必须引用 Question。练习导入识别出的题目经过结构化校验后创建或复用 Question，再记录本次作答。题库不保存“我这次做得怎么样”。

## 6. 与错题系统的关系

错题只是题库题目在某次练习或单题导入中产生的复盘视图。Mistake 可以引用 Question 并保存错因、解析、我的答案等特有信息；Question 不因产生 Mistake 而改变为“错题”。

## 7. 与复习系统的关系

Review Item 使用 `target_type/target_id`。第一版优先支持 `mistake` 与 `knowledge_point`；`question` 已在枚举中保留，但直接复习题目可后续启用，不能让题库拥有调度算法。

## 8. 与 AI 系统的关系

AI 可识别、拆分、规范化题目并给出去重候选。结果写入 AI Run 并经过 schema 校验；创建、合并或覆盖正式 Question 前必须由用户确认。

## 9. 页面与 API

- 页面：`/manage/questions`、`/manage/questions/[id]`。
- API：`GET/POST /api/admin/questions`，`GET/PUT/DELETE /api/admin/questions/{id}`。
- 页面和 API 默认私有，全部依赖管理员身份。

## 10. 第一版范围

- 题目 CRUD、来源、学科、难度、知识点与默认私有可见性。
- 被练习与错题引用。
- 规范化 hash 只用于提示可能重复，不自动合并。

## 11. 暂缓能力

- 公共题库发布、协作编辑、复杂版本树、外部题库双向同步。
- 基于向量的自动合并和 Question 直接进入复习。
