# ADR-001：PostgreSQL 是唯一事实来源

- 状态：Accepted
- 日期：2026-07-13
- 范围：Content、Knowledge、Learning、Review、AI、Publish

## 决策

正式业务数据统一以 PostgreSQL 为唯一事实来源。GitHub Markdown、静态文件和导出文件只承担版本归档、公开站点构建输入、导出和灾难恢复副本职责。

## 原因

同时维护数据库、GitHub 和 Markdown 主数据会造成删除不同步、旧内容残留、版本漂移和无法判断的写入优先级。

## 后果

所有写入必须经过后端 service；导出和发布必须带源版本；迁移必须记录哈希、冲突、回滚和只读归档。短期需要保留旧同步作为兼容层，但不能继续让它独立写正式数据。

