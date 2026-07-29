from pathlib import Path
import uuid

import httpx
from sqlalchemy import delete, select

import main
from app.database import async_session, engine
from app.models.attachment import Attachment
from app.models.capture import CaptureItem
from app.models.note import User
from app.routers.auth import get_current_admin


TEST_ADMIN_ID = uuid.UUID("23247a68-7a00-4464-9d96-948c018fdffe")

MINIMAL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01"
    b"\x5c\xcd\xff\x69\x00\x00\x00\x00IEND\xaeB`\x82"
)


async def _admin_override():
    return User(id=TEST_ADMIN_ID, username="i6-http-admin", is_admin=True)


async def _cleanup_capture_and_attachment(attachment_id: uuid.UUID) -> None:
    async with async_session() as session:
        attachment = await session.scalar(
            select(Attachment).where(Attachment.id == attachment_id)
        )
        if attachment is None:
            return
        storage_path = Path(main.get_settings().UPLOAD_ROOT) / attachment.storage_key
        await session.execute(
            delete(CaptureItem).where(
                CaptureItem.source_attachment_id == attachment_id
            )
        )
        await session.execute(delete(Attachment).where(Attachment.id == attachment_id))
        await session.commit()
    storage_path.unlink(missing_ok=True)


async def _exercise_admin_upload_and_capture() -> None:
    main.app.dependency_overrides[get_current_admin] = _admin_override
    attachment_id = None
    try:
        await main.validate_database_readiness()
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            upload = await client.post(
                "/api/admin/attachments",
                files={"file": ("i6-capture.png", MINIMAL_PNG, "image/png")},
            )
            assert upload.status_code == 201
            attachment_id = uuid.UUID(upload.json()["id"])
            assert upload.json()["visibility"] == "private"
            assert upload.json()["status"] == "active"

            capture = await client.post(
                "/api/admin/captures",
                json={"attachment_id": str(attachment_id)},
            )
            assert capture.status_code == 201
            assert capture.json()["status"] == "uploaded"
            assert capture.json()["source_attachment_id"] == str(attachment_id)
    finally:
        if attachment_id is not None:
            await _cleanup_capture_and_attachment(attachment_id)
        main.app.dependency_overrides.pop(get_current_admin, None)
        await engine.dispose()


def test_admin_can_upload_private_image_and_create_capture():
    import asyncio

    asyncio.run(_exercise_admin_upload_and_capture())


async def _exercise_invalid_upload() -> None:
    main.app.dependency_overrides[get_current_admin] = _admin_override
    try:
        upload_root = Path(main.get_settings().UPLOAD_ROOT)
        await main.validate_database_readiness()
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/admin/attachments",
                files={"file": ("i6-capture.exe", b"not-an-image", "application/octet-stream")},
            )
        assert 400 <= response.status_code < 500
        assert not list(upload_root.glob(".attachment-*.tmp"))
    finally:
        main.app.dependency_overrides.pop(get_current_admin, None)
        await engine.dispose()


def test_invalid_upload_is_rejected_and_does_not_leave_temp_file():
    import asyncio

    asyncio.run(_exercise_invalid_upload())
