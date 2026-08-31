# Capture Router 上传识别路由器

> 状态：拟新增；第一版建议。

## 职责

用户只负责上传，Capture Router 根据 OCR 结果、文件特征和规则判断内容属于题目、错题、练习、知识材料、普通附件或未知。它只生成分类结果和草稿，不直接写正式业务表。

## 检测类型与表

检测类型：`question_only`、`mistake_candidate`、`practice_session_candidate`、`knowledge_material`、`note_attachment`、`unknown`。

核心表：`capture_jobs`、`capture_results`。结果保存各类型分数、规则版本、证据、警告和关联 OCR 结果。

## 第一版路由规则

- `question_score >= 0.75` 且 practice/mistake 均 `< 0.60`：生成 `question_draft`。
- `mistake_score >= 0.70`，或 question `>= 0.65` 且检测到错误答案/批改痕迹：生成 question + mistake drafts。
- `practice_score >= 0.70`，或题目数 `>= 3` 且有多个作答/批改结果：创建 `practice_import_job`。
- knowledge material `>= 0.70` 且 question `< 0.50`：保存为笔记附件并生成知识点建议。
- 最高分 `< 0.65`：标记 `unknown`，进入人工分流。

阈值是第一版建议，必须配置化并记录规则版本；规则冲突时不得猜测正式类型。

## 第一版范围

图片/PDF 的规则分类、置信度、证据、人工改类、幂等重跑和 draft 输出。

## 暂缓范围

音视频、压缩包、端到端自动入库、复杂在线学习和自动知识图谱。
