# Checklist

- [x] 已建立对应 workflow，并由用户批准 tasks。
- [x] 已明确独立错题模型与当前 `Note(type="mistake")` 的关系。
- [x] 可以从正式题目创建错题草稿。
- [x] 错题草稿可关联 question 或 question draft。
- [x] 草稿可人工审核并只生成一个正式错题。
- [x] active 错题生成简单复习项。
- [x] 管理端错题列表与详情可用。
- [x] 管理端待复习列表可用。
- [x] 完成复习会生成记录并更新下一次复习时间。
- [x] 未确认错题不进入复习。
- [x] 公开错题读取未受损，管理操作均受保护。
- [x] 未实现 BKT、完整练习或自动判错。
- [x] 已填写 `handoff.md`。

## 验证备注

- 自动验证通过：TypeScript、production build、定向后端测试、diff whitespace check。
- 真实浏览器完整闭环、移动视口与登录态操作仍等待用户验收；详见 workflow `validation.md`
  与 `audit.md`。
