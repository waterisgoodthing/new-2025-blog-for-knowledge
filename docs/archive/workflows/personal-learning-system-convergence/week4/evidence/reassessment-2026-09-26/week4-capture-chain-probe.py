import asyncio, io, json, logging
from unittest.mock import AsyncMock, patch
import httpx
from app.services.capture_recognition import recognize_image
from app.services.capture_ai_draft import draft_mistake
from app.schemas.capture import CaptureDraftInput

async def check(name, provider_outcome):
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    root = logging.getLogger()
    root.addHandler(handler)
    providers = [{'name': 'probe1', 'model': 'fake'}, {'name': 'probe2', 'model': 'fake'}]
    fake = AsyncMock(side_effect=provider_outcome) if isinstance(provider_outcome, Exception) else AsyncMock(return_value=provider_outcome)
    try:
        with patch('app.services.ai_service._select_providers', return_value=providers), patch('app.services.ai_service._call_provider', new=fake), patch('app.services.ai_gateway._start_run_record', new=AsyncMock(return_value=None)), patch('app.services.ai_gateway._finish_run_record', new=AsyncMock()), patch('app.services.ai_gateway._write_call_log', new=AsyncMock()) as writer:
            result = await recognize_image(b'probe-image', 'image/png', capture_id='capture-probe')
            record = writer.await_args.args[1]
        logs = buffer.getvalue()
        print(json.dumps({'case': name, 'code': result.error_code, 'category': result.failure_category, 'provider_calls': fake.await_count, 'log_leaks_synthetic_marker': 'SYNTHETIC_SECRET_8Z' in logs, 'persisted_error_leaks_synthetic_marker': 'SYNTHETIC_SECRET_8Z' in (record.error or ''), 'gateway_error': record.error, 'logs': logs}, ensure_ascii=False))
    finally:
        root.removeHandler(handler)

async def main():
    await check('native_httpx_ReadTimeout_empty_message', httpx.ReadTimeout(''))
    await check('malformed_provider_JSON', {'choices': [{'message': {'content': 'not json'}}]})
    await check('HTTP_503_raw_provider_error', RuntimeError('AI API error (503): {"api_key":"SYNTHETIC_SECRET_8Z"}'))

asyncio.run(main())
