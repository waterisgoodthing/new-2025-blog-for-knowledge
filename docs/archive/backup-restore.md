# 数据备份与恢复流程

## 1. 数据库备份

### 自动备份 (每日)

```bash
# crontab -e
0 3 * * * pg_dump -U user -d blog_db -F c -f /backup/blog_db_$(date +\%Y\%m\%d).dump
```

### 手动备份

```bash
pg_dump -U user -d blog_db -F c -f backup_$(date +%Y%m%d_%H%M%S).dump
```

## 2. 图片备份

### 本地图片目录

```bash
rsync -av --delete /app/uploads/ /backup/images/
```

### 对象存储 (如使用 R2/OSS)

- 启用版本控制
- 设置生命周期策略: 保留 30 天删除标记

## 3. 恢复流程

### 数据库恢复

```bash
pg_restore -U user -d blog_db -c backup.dump
# -c 表示先清理现有对象
```

跨环境恢复到临时库或新机器时，建议去掉源库 owner/ACL，避免目标环境没有同名角色导致恢复失败：

```bash
pg_restore --no-owner --no-acl -U user -d blog_db backup.dump
```

### 图片恢复

```bash
rsync -av /backup/images/ /app/uploads/
```

## 4. 验证清单

- [ ] 备份文件存在且大小合理
- [ ] 恢复后 `SELECT count(*) FROM notes` 数量正确
- [ ] 恢复后图片 URL 可访问
- [ ] 恢复后 AI 分析字段 (`ai_metadata`) 保留
- [ ] 恢复后文件夹结构保留

## 4.1 恢复演练记录

### 2026-06-03

- 备份命令: `pg_dump -Fc`
- 恢复方式: 独立临时 PostgreSQL 数据目录 + 临时数据库
- 恢复命令: `pg_restore --no-owner --no-acl`
- 验证结果:
  - 备份文件生成成功，大小约 25 KB。
  - 临时库恢复成功。
  - `public` schema 表数量: 10。
  - `alembic_version`: `005`。
- 经验记录:
  - 当前业务 DB 用户没有 `CREATE DATABASE` 权限，因此不能直接在主 PostgreSQL 实例创建临时恢复库。
  - 跨环境恢复时必须加 `--no-owner --no-acl`，否则 dump 中的 `blog_user` owner/GRANT 会导致目标临时库恢复失败。

## 5. 备份存储位置

| 数据 | 位置 | 频率 | 保留 |
|------|------|------|------|
| PostgreSQL | 本地 + 异地 | 每日 | 30 天 |
| 图片 | 对象存储版本控制 | 实时 | 30 天 |
| 配置 | Git | 每次变更 | 永久 |

## 6. 公开导出分离

- **公开导出**: GitHub sync 只导出 `status=published` + `hidden=false` 的博客
- **私有备份**: `pg_dump` 包含所有数据（含私有笔记、错题、草稿）
- 两者分离: 公开导出通过 `sync.py`，私有备份通过 `pg_dump`
