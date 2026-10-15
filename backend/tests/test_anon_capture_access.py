"""匿名访问拒绝测试 + 公开 API 回归测试。

使用 FastAPI TestClient，不需要启动实际服务器。
"""

from fastapi.testclient import TestClient

import main

ANON_ENDPOINTS = [
    ("GET", "/api/admin/captures", None),
    ("POST", "/api/admin/captures", {"attachment_id": "00000000-0000-0000-0000-000000000000"}),
    ("GET", "/api/admin/captures/00000000-0000-0000-0000-000000000000", None),
    ("PATCH", "/api/admin/captures/00000000-0000-0000-0000-000000000000", {}),
    ("POST", "/api/admin/captures/00000000-0000-0000-0000-000000000000/recognize", None),
    ("POST", "/api/admin/captures/00000000-0000-0000-0000-000000000000/draft", None),
    (
        "POST",
        "/api/admin/captures/00000000-0000-0000-0000-000000000000/convert",
        {"subject_id": 1, "question_text": "test"},
    ),
]


def test_anon_capture_endpoints_denied():
    """所有 capture 端点在无 Authorization header 时必须返回 401 或 403。"""
    with TestClient(main.app) as client:
        for method, path, body in ANON_ENDPOINTS:
            if method == "GET":
                resp = client.get(path)
            elif method == "POST":
                resp = client.post(path, json=body) if body else client.post(path)
            elif method == "PATCH":
                resp = client.patch(path, json=body) if body else client.patch(path)
            else:
                continue
            assert resp.status_code in (401, 403), (
                f"{method} {path} -> {resp.status_code} (expected 401/403)"
            )


def test_public_notes_api_works():
    """公开 GET /api/notes 不应因 capture 路由而受影响。

    TestClient 必须作为 context manager 使用，以便 FastAPI lifespan
    在其事件循环关闭前 dispose async engine。
    """
    with TestClient(main.app) as client:
        resp = client.get("/api/notes")
        assert resp.status_code == 200
