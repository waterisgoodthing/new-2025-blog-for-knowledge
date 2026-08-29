from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import main
from app.routers.auth import _require_operator_key

AUTH_SOURCE = Path(__file__).parents[1] / "app" / "routers" / "auth.py"


def _settings(**overrides) -> SimpleNamespace:
    base = {
        "ENV": "staging",
        "JWT_SECRET_KEY": "secure-test-key",
        "ALLOWED_ORIGINS": "https://example.test",
        "AUTH_BYPASS": "false",
        "AUTH_BYPASS_ALLOW": "false",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_non_production_environment_rejects_the_default_jwt_secret() -> None:
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        main.validate_security_settings(_settings(JWT_SECRET_KEY="your-secret-key-change-this"))


def test_non_production_environment_rejects_active_auth_bypass() -> None:
    with pytest.raises(RuntimeError, match="AUTH_BYPASS"):
        main.validate_security_settings(_settings(AUTH_BYPASS="true", AUTH_BYPASS_ALLOW="true"))


def test_non_production_environment_rejects_wildcard_cors() -> None:
    with pytest.raises(RuntimeError, match="CORS"):
        main.validate_security_settings(_settings(ALLOWED_ORIGINS="*"))


def test_non_production_environment_rejects_missing_cors_configuration() -> None:
    with pytest.raises(RuntimeError, match="CORS"):
        main.validate_security_settings(_settings(ALLOWED_ORIGINS=""))


def test_non_production_environment_rejects_whitespace_only_cors() -> None:
    with pytest.raises(RuntimeError, match="CORS"):
        main.validate_security_settings(_settings(ALLOWED_ORIGINS="   "))


def test_production_still_rejects_enabled_public_registration() -> None:
    with pytest.raises(RuntimeError, match="ENABLE_REGISTRATION"):
        main.validate_security_settings(_settings(ENV="production", ENABLE_REGISTRATION=True))


@pytest.mark.parametrize("env", ["development", "dev", "local", "test"])
def test_development_environments_keep_bypass_semantics(env: str) -> None:
    main.validate_security_settings(
        _settings(
            ENV=env,
            JWT_SECRET_KEY="your-secret-key-change-this",
            AUTH_BYPASS="true",
            AUTH_BYPASS_ALLOW="true",
        )
    )


def test_pinned_revision_matches_the_newest_migration() -> None:
    assert main.EXPECTED_ALEMBIC_REVISION == "026"


def test_orphaned_passkey_registration_options_endpoint_is_removed() -> None:
    paths = {getattr(route, "path", None) for route in main.app.routes}
    assert "/api/auth/passkey/reg-options" not in paths


def test_public_passkey_status_endpoint_is_retained_for_the_login_page() -> None:
    paths = {getattr(route, "path", None) for route in main.app.routes}
    assert "/api/auth/passkey/status" in paths


def test_operator_key_accepts_the_configured_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routers.auth.get_settings",
        lambda: SimpleNamespace(OPERATOR_REGISTRATION_KEY="operator-secret"),
    )
    _require_operator_key("operator-secret")


def test_operator_key_rejects_a_wrong_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routers.auth.get_settings",
        lambda: SimpleNamespace(OPERATOR_REGISTRATION_KEY="operator-secret"),
    )
    with pytest.raises(HTTPException) as excinfo:
        _require_operator_key("operator-wrong")
    assert excinfo.value.status_code == 403


def test_operator_key_rejects_a_missing_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routers.auth.get_settings",
        lambda: SimpleNamespace(OPERATOR_REGISTRATION_KEY="operator-secret"),
    )
    with pytest.raises(HTTPException) as excinfo:
        _require_operator_key(None)
    assert excinfo.value.status_code == 403


def test_operator_key_rejects_when_not_configured(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.routers.auth.get_settings",
        lambda: SimpleNamespace(OPERATOR_REGISTRATION_KEY=""),
    )
    with pytest.raises(HTTPException) as excinfo:
        _require_operator_key("operator-secret")
    assert excinfo.value.status_code == 403


def test_shared_keys_are_compared_in_constant_time() -> None:
    source = AUTH_SOURCE.read_text(encoding="utf-8")
    assert "import secrets" in source
    assert source.count("secrets.compare_digest(") >= 2
