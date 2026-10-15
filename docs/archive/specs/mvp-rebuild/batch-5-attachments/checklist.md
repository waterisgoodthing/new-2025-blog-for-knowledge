# Checklist

- [x] 已建立对应 workflow，并由用户批准 tasks。
- [x] 管理员本地上传可用。
- [x] 文件元数据、storage provider 与 storage key 正确保存。
- [x] 附件列表与详情预览可用。
- [x] 附件可关联草稿、题目和错题。
- [x] 附件默认 private。
- [x] 上传和私有读取具有后端管理员保护。
- [x] 数据库与 API 不泄露绝对本地路径。
- [x] 业务归属通过 attachment links 表达。
- [x] 失败、无权限、缺失文件和不可预览状态已验证。
- [x] 未实现 OCR、对象存储或 PDF 自动解析。
- [x] 已填写 `handoff.md`。

## 验证备注

- 自动验证通过：后端附件 service/route 测试、TypeScript、production build、diff whitespace check。
- 真实浏览器上传/预览/关联仍等待用户验收；详见 workflow `validation.md` 与 `audit.md`。
