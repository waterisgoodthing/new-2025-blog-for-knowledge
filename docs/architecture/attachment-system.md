# Attachment System 附件系统

> 状态：拟新增；所有学习附件默认私有。

## 职责

附件系统保存上传文件元数据、存储引用、校验值、缩略图、派生文件和业务关联，是 OCR、Capture、练习导入和公开媒体的原始材料来源层。

## 核心表

- `attachments`：`id`、文件名、MIME、大小、hash、存储键、可见性、扫描状态、创建时间。
- `attachment_links`：附件与 Post、Note、Question、Practice、Mistake 等实体的关联和用途。
- `attachment_derivatives`：缩略图、PDF 拆页、预览图及派生状态。

`attachments` 只保存文件本体元数据，不保存业务对象引用。所有附件与业务对象的关联统一由 `attachment_links(attachment_id, target_type, target_id, purpose)` 表达；`source_type/source_id` 如出现只用于来源追踪，不用于当前目标引用。同一文件因此可以被安全复用，也能在删除前统一检查引用。

## 隐私边界

允许公开：博客封面、公开文章内图片、管理员明确设为 public 的媒体。

永远私有：练习截图、错题照片、试卷/讲义 PDF、OCR 原文、AI 识别来源图。API 不返回本地路径、存储键或内部临时 URL；公开 URL 必须经受控映射。

## 第一版范围

图片/PDF 上传、类型与大小校验、hash 去重提示、文件元数据、`attachment_links`、缩略图、私有下载授权和删除引用检查。

## 暂缓范围

音视频解析、压缩包解包、公共素材库、跨用户共享和复杂内容分发。
