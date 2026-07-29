# I10 需求与验收

- 来源、哈希、映射、冲突与 owner/schema authority 均有证据。
- `DRY_RUN_READY` 必须逐项 PASS；任一 UNKNOWN/BLOCKED 停止写入。
- 隔离 dry-run 可核对、可回滚、可销毁，且无源库写入。
