# Design Review Checklist

## 现状证据

- [x] 已检查 `backend/app/routers/ai.py`
- [x] 已检查 `backend/app/services/ai_gateway.py`
- [x] 已检查 `backend/app/services/ai_run_service.py`
- [x] 已检查 `backend/app/services/ai_analyze_service.py`
- [x] 已检查 `backend/app/models/ai_run.py`
- [x] 已检查 `backend/app/schemas/ai_run.py`
- [x] 已搜索 `backend/tests/`
- [x] 已检查 `src/lib/api/`
- [x] 已确认实际 manage route-group 路径
- [x] 已定位两个 stream endpoint 的前端调用
- [x] 已确认 UI 不消费逐 token 输出
- [x] 已确认 `call_stream()` 是同步包装
- [x] 已确认 endpoint generator 实际调用 `call_text` / `call_vision`
- [x] 已确认 stream task type 未注册到 `AiTaskType`
- [x] 已确认现有 Run 状态无 interrupted/cancelled
- [x] 已确认当前无 `ai_run_artifacts` 模型/表

## 设计决策

- [x] 已比较接入与暂不接入方案
- [x] 已推荐暂不接入现有伪流式 endpoint
- [x] 已给出未来方案 A 的最小状态机
- [x] 已区分 provider、parser、generator 与 disconnect
- [x] 已选择不保存 partial output
- [x] 已定义 final output 安全边界
- [x] 已评估前端与管理页影响
- [x] 已说明 migration 与状态枚举条件
- [x] 已说明不阻塞 Batch 12

## 本轮边界

- [x] 未修改 `backend/app`
- [x] 未修改 `src`
- [x] 未修改 tests
- [x] 未新增 migration 或数据库表
- [x] 未改 `ai_runs` / `ai_call_logs`
- [x] 未调用真实 provider
- [x] 未执行真实流式调用
- [x] 已声明 RISK-B11-003 的关闭方式：正式链路迁出伪流式 endpoint；未声明真实 provider token streaming 审计完成
- [x] 未进入 Batch 12
