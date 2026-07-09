# 练习系统设计

> 状态：目标架构，待实现或待迁移。

## 1. 系统定位

练习系统记录用户今天做了什么题、怎样作答、结果如何以及本次练习的分析报告。练习导入不等于错题导入；错题只是部分练习结果。

## 2. 系统职责

- 管理 Practice Session 和逐题 Practice Attempt。
- 编排图片、PDF、文本和批改结果的练习导入。
- 保存正确、错误、半对、评分、耗时、警告和分析。
- 生成 Mistake Draft 与 Practice Report，并保留可追溯来源。

## 3. 不负责的内容

- 不维护正式错题内容，不拥有复习算法。
- 不负责题目本体去重规则或 AI 模型调用底层实现。
- 不把 AI 输出直接当作正式错题或正式复习计划。

## 4. 核心实体

- `practice_sessions`：一次练习及汇总。
- `practice_attempts`：一次练习中某道题的作答。
- `practice_import_jobs`、`practice_import_files`：导入生命周期和原始文件。
- `practice_reports`：本次练习报告与建议。
- `mistake_drafts`：待用户确认的错题候选。

## 5. 练习导入流程

```text
上传图片 / PDF / 文本
↓
创建 practice_session
↓
创建 practice_import_job
↓
AI 识别题目
↓
生成 questions
↓
生成 practice_attempts
↓
判断正确、错误、半对
↓
生成 mistake_drafts
↓
用户审核
↓
转换为 mistakes
↓
加入 review_items
↓
生成 practice_report
```

失败状态必须可重试；确认请求必须幂等并校验输入版本。AI 输出必须经过用户确认。

## 6. 作答记录

Practice Attempt 记录本次答案、正确答案、`result_type`、评分、耗时、错因候选、置信度和警告。它记录“我这次做得怎么样”，无论做对还是做错都应保留。`result_type` 是权威字段，不再只依赖 `is_correct`。

作答结果统一为 `correct`、`wrong`、`partial`、`unknown`、`skipped`：

- `wrong`：生成错题草稿或 `unconfirmed` 候选。
- `partial`：生成错题草稿，但必须确认。
- `unknown`：保留作答，不自动生成错题。
- `correct` / `skipped`：默认不进入错题系统。

## 7. 练习报告

Practice Report 汇总正确率、薄弱知识点、错误类型和复习建议，并关联 AI Run。报告和建议不是正式 Review Schedule，采纳需要独立动作。

## 8. 错题草稿生成

错误或需要复盘的 Attempt 可生成 Mistake Draft。用户可以修正、拒绝或确认；只有确认转换后才创建正式 Mistake，之后才可显式创建 Review Item。

## 9. 与题库系统的关系

题库保存题目本体，Practice Attempt 引用 Question。导入时先匹配或创建 Question，再保存本次作答；题目复用不合并不同作答。

## 10. 与错题系统的关系

Practice System 只输出 Mistake Draft 与来源证据。Mistake System 拥有正式错题、错因、解析、状态和编辑能力，不保存完整练习或做对题目的历史。

## 11. 与复习系统的关系

Practice Report 可以提出复习建议，已确认 Mistake 可以加入 Review Item。Review System 独立负责计划、今日队列、逾期、评分、记录和算法状态。

## 12. 与 AI 系统的关系

AI 负责识别题目与答案、识别批改痕迹、拆题、批改、错因分析、知识点归纳、报告和建议。每次运行落 `ai_runs`；Practice Service 校验结构并编排草稿，AI Service 不直接写正式业务数据。

## 13. 页面与 API

- 页面：`/manage/practice`、`/manage/practice/import`、`/manage/practice/[sessionId]`、`/manage/practice/[sessionId]/review`。
- API：Practice Session、Attempt、Import Job、Report 与 Mistake Draft admin API。
- 所有页面和 API 默认私有，并受 `get_current_admin` 保护。

## 14. 第一版范围

- 图片、PDF、文本导入；练习与作答记录；人工校正。
- 正确/错误/半对判断；错题草稿确认；基础练习报告。
- 可重试任务、来源追踪、审计和 AI Run 关联。

## 15. 暂缓能力

- 自动生成正式复习计划、无确认自动入错题库。
- 多用户班级、实时考试、排名、公共练习分享和复杂阅卷协作。
