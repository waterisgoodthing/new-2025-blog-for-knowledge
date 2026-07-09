"""AI Gateway 单元测试 — Batch 9。

覆盖：
- call_text 成功路径（验证日志写入）
- call_text 失败路径（验证失败日志写入）
- fallback 路径（验证 attempts 记录）
- 日志写入失败不阻塞主调用
- input_summary / error 截断
"""

import unittest
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.ai_gateway import (
    GatewayCallResult,
    _build_failure_result,
    _build_success_result,
    _serialize_attempts,
    _write_call_log,
    call_text,
    call_vision,
    call_general,
)
from app.services.ai_service import CallResult, ProviderAttempt
from app.services.ai_task_types import AiTaskType


class CallTextSuccessTest(unittest.IsolatedAsyncioTestCase):
    """测试 call_text 成功路径。"""

    async def test_call_text_success_returns_correct_result(self):
        """成功调用返回 GatewayCallResult(success=True)，日志被写入。"""
        mock_result = CallResult(
            data={"title": "test"},
            attempts=[
                ProviderAttempt(
                    provider="deepseek",
                    model="deepseek-v4-pro",
                    success=True,
                    latency_ms=500,
                )
            ],
            provider_used="deepseek",
            fallback_used=False,
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ) as mock_log,
        ):
            gw = await call_text("test_task", [{"role": "user", "content": "hi"}])

        self.assertTrue(gw.success)
        self.assertEqual(gw.data, {"title": "test"})
        self.assertEqual(gw.provider_used, "deepseek")
        self.assertEqual(gw.model, "deepseek-v4-pro")
        self.assertFalse(gw.fallback_used)
        self.assertIsNone(gw.error)
        self.assertEqual(gw.attempts[0]["provider"], "deepseek")
        self.assertEqual(gw.attempts[0]["model"], "deepseek-v4-pro")
        # 日志写入被调用
        mock_log.assert_called_once()
        call_args = mock_log.call_args
        self.assertEqual(call_args[0][0], "test_task")
        self.assertEqual(call_args[0][1], gw)
        self.assertIsNone(call_args[0][2])  # input_summary=None by default

    async def test_call_text_passes_input_summary_to_log(self):
        """input_summary 正确传递到日志写入。"""
        mock_result = CallResult(
            data="ok",
            attempts=[ProviderAttempt(provider="deepseek", model="m1", success=True)],
            provider_used="deepseek",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ) as mock_log,
        ):
            await call_text(
                "test_task",
                [{"role": "user", "content": "hi"}],
                input_summary="summary text",
            )

        call_args = mock_log.call_args
        self.assertEqual(call_args[0][2], "summary text")

    async def test_registered_task_records_business_run_without_changing_result(self):
        mock_result = CallResult(
            data={"question_text": "q"},
            attempts=[ProviderAttempt(provider="deepseek", model="m1", success=True)],
            provider_used="deepseek",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ),
            patch(
                "app.services.ai_gateway._start_run_record",
                new_callable=AsyncMock,
                return_value="run-id",
            ) as start_run,
            patch(
                "app.services.ai_gateway._finish_run_record",
                new_callable=AsyncMock,
            ) as finish_run,
        ):
            result = await call_text(
                AiTaskType.CAPTURE_DRAFT,
                [{"role": "user", "content": "hi"}],
                input_summary="safe",
            )

        self.assertTrue(result.success)
        start_run.assert_awaited_once()
        finish_run.assert_awaited_once_with(
            "run-id",
            AiTaskType.CAPTURE_DRAFT.value,
            result,
        )

    async def test_formal_analyze_text_task_records_call_log_and_run(self):
        mock_result = CallResult(
            data={"title": "ok", "question": "q"},
            attempts=[ProviderAttempt(provider="deepseek", model="m1", success=True)],
            provider_used="deepseek",
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ) as write_call_log,
            patch(
                "app.services.ai_gateway._start_run_record",
                new_callable=AsyncMock,
                return_value="run-id",
            ) as start_run,
            patch(
                "app.services.ai_gateway._finish_run_record",
                new_callable=AsyncMock,
            ) as finish_run,
        ):
            result = await call_text(
                AiTaskType.ANALYZE_TEXT,
                [{"role": "user", "content": "题目文本"}],
                input_summary="safe text summary",
            )

        self.assertTrue(result.success)
        write_call_log.assert_awaited_once()
        self.assertEqual(write_call_log.await_args.args[0], AiTaskType.ANALYZE_TEXT.value)
        start_run.assert_awaited_once()
        self.assertEqual(start_run.await_args.args[0], AiTaskType.ANALYZE_TEXT.value)
        finish_run.assert_awaited_once_with(
            "run-id",
            AiTaskType.ANALYZE_TEXT.value,
            result,
        )


class CallTextFailureTest(unittest.IsolatedAsyncioTestCase):
    """测试 call_text 失败路径。"""

    async def test_call_text_failure_returns_error_result(self):
        """_call_with_fallback 抛异常时，返回 GatewayCallResult(success=False)。"""
        exc = RuntimeError("provider unavailable")

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                side_effect=exc,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ) as mock_log,
        ):
            gw = await call_text("test_task", [{"role": "user", "content": "hi"}])

        self.assertFalse(gw.success)
        self.assertIsNone(gw.data)
        self.assertEqual(gw.provider_used, "")
        self.assertEqual(gw.model, "")
        self.assertEqual(gw.error, "provider unavailable")
        self.assertEqual(gw.attempts, [])
        # 日志仍被写入（失败也要记录）
        mock_log.assert_called_once()

    async def test_call_vision_failure_writes_log(self):
        """call_vision 失败也写入日志。"""
        exc = ValueError("no vision provider")

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                side_effect=exc,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ) as mock_log,
        ):
            gw = await call_vision("ocr_task", [{"role": "user", "content": "image"}])

        self.assertFalse(gw.success)
        self.assertEqual(gw.error, "no vision provider")
        mock_log.assert_called_once()


class FallbackPathTest(unittest.IsolatedAsyncioTestCase):
    """测试 fallback 路径。"""

    async def test_fallback_records_attempts(self):
        """fallback 时 attempts 包含所有尝试，fallback_used=True。"""
        mock_result = CallResult(
            data={"result": "ok"},
            attempts=[
                ProviderAttempt(
                    provider="deepseek",
                    model="deepseek-v4-pro",
                    success=False,
                    latency_ms=300,
                    error="rate limit",
                ),
                ProviderAttempt(
                    provider="qwen_general",
                    model="qwen3.7-plus",
                    success=True,
                    latency_ms=800,
                    fallback_used=True,
                ),
            ],
            provider_used="qwen_general",
            fallback_used=True,
        )

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch(
                "app.services.ai_gateway._write_call_log",
                new_callable=AsyncMock,
            ),
        ):
            gw = await call_general("general_task", [{"role": "user", "content": "hi"}])

        self.assertTrue(gw.success)
        self.assertTrue(gw.fallback_used)
        self.assertEqual(gw.provider_used, "qwen_general")
        self.assertEqual(gw.model, "qwen3.7-plus")
        # attempts 包含 2 条记录
        self.assertEqual(len(gw.attempts), 2)
        self.assertEqual(gw.attempts[0]["provider"], "deepseek")
        self.assertFalse(gw.attempts[0]["success"])
        self.assertEqual(gw.attempts[0]["error"], "rate limit")
        self.assertEqual(gw.attempts[1]["provider"], "qwen_general")
        self.assertTrue(gw.attempts[1]["success"])

    async def test_serialize_attempts_truncates_error(self):
        """_serialize_attempts 截断 error 到 200 字符。"""
        long_error = "x" * 300
        attempts = [
            ProviderAttempt(
                provider="deepseek",
                model="m",
                success=False,
                error=long_error,
            )
        ]
        result = _serialize_attempts(attempts)
        self.assertEqual(len(result[0]["error"]), 200)


class LogWriteFailureTest(unittest.IsolatedAsyncioTestCase):
    """测试日志写入失败不阻塞主调用。"""

    async def test_log_write_failure_does_not_block(self):
        """_write_call_log 内部 commit 失败时，call_text 仍正常返回。

        _write_call_log 设计为 catch 所有异常，因此 call_text 不会因
        日志写入失败而中断。
        """
        mock_result = CallResult(
            data={"ok": True},
            attempts=[ProviderAttempt(provider="deepseek", model="m1", success=True)],
            provider_used="deepseek",
        )

        # mock async_session 让 commit 抛异常，模拟 DB 故障
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.commit.side_effect = Exception("DB connection failed")

        with (
            patch(
                "app.services.ai_gateway._call_with_fallback",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
            patch("app.services.ai_gateway.async_session", return_value=mock_session),
        ):
            gw = await call_text("test_task", [{"role": "user", "content": "hi"}])

        # 主调用不受影响
        self.assertTrue(gw.success)
        self.assertEqual(gw.data, {"ok": True})
        # commit 被调用（即使失败）
        mock_session.commit.assert_called_once()

    async def test_write_call_log_catches_exception(self):
        """_write_call_log 内部异常被 catch，不传播。"""
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.commit.side_effect = Exception("commit failed")

        with patch("app.services.ai_gateway.async_session", return_value=mock_session):
            # 不应抛异常
            result = GatewayCallResult(
                data={"ok": True},
                provider_used="deepseek",
                model="m1",
                latency_ms=100,
                success=True,
                fallback_used=False,
                attempts=[],
            )
            await _write_call_log("test", result, "summary")

        # commit 被调用
        mock_session.commit.assert_called_once()


class TruncationTest(unittest.IsolatedAsyncioTestCase):
    """测试 input_summary / error 截断。"""

    async def test_input_summary_truncated_in_write_call_log(self):
        """_write_call_log 截断 input_summary 到 200 字符。"""
        long_summary = "x" * 300
        captured_log = {}

        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session

        def capture_add(log_obj):
            captured_log["task_type"] = log_obj.task_type
            captured_log["input_summary"] = log_obj.input_summary
            captured_log["error"] = log_obj.error

        mock_session.add = MagicMock(side_effect=capture_add)

        result = GatewayCallResult(
            data=None,
            provider_used="",
            model="",
            latency_ms=0,
            success=False,
            fallback_used=False,
            attempts=[],
            error="x" * 600,
        )

        with patch("app.services.ai_gateway.async_session", return_value=mock_session):
            await _write_call_log("test", result, long_summary)

        self.assertEqual(len(captured_log["input_summary"]), 200)
        self.assertEqual(len(captured_log["error"]), 500)

    def test_build_failure_result_truncates_error(self):
        """_build_failure_result 截断 error 到 500 字符。"""
        long_error = "y" * 800
        result = _build_failure_result(RuntimeError(long_error), 100)
        self.assertEqual(len(result.error), 500)
        self.assertFalse(result.success)

    def test_build_success_result_extracts_model_from_attempts(self):
        """_build_success_result 从 attempts 中提取 model。"""
        mock_result = CallResult(
            data={"ok": True},
            attempts=[
                ProviderAttempt(
                    provider="deepseek", model="deepseek-v4-pro", success=False
                ),
                ProviderAttempt(
                    provider="qwen_general",
                    model="qwen3.7-plus",
                    success=True,
                    fallback_used=True,
                ),
            ],
            provider_used="qwen_general",
            fallback_used=True,
        )
        gw = _build_success_result(mock_result, 500)
        self.assertEqual(gw.model, "qwen3.7-plus")
        self.assertTrue(gw.success)


if __name__ == "__main__":
    unittest.main()
