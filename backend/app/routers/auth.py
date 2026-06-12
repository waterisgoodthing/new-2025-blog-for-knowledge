from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.note import User
from app.models.session import AdminSession, AdminPassword
from app.schemas.auth import (
    LoginRequest,
    OperatorRegOptionsRequest,
    OperatorRegisterRequest,
    OperatorRegisterResponse,
    RegisterRequest,
    SessionUserOut,
    SetPasswordRequest,
    UserOut,
)
from app.utils.auth import (
    PASSKEY_SESSION_DAYS,
    PASSWORD_SESSION_DAYS,
    generate_session_token,
    get_session_expiry,
    hash_password,
    hash_session_token,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

logger = logging.getLogger(__name__)

SESSION_COOKIE_NAME = "admin_session"
COOKIE_PATH = "/api"
COOKIE_SAMESITE = "lax"


def _is_secure_request(request: Request) -> bool:
    return request.url.scheme == "https"


def _set_session_cookie(response: JSONResponse, token: str, request: Request, max_age: int) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=_is_secure_request(request),
        samesite=COOKIE_SAMESITE,
        path=COOKIE_PATH,
    )


def _clear_session_cookie(response: JSONResponse) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path=COOKIE_PATH)


def _is_auth_bypass_active() -> bool:
    settings = get_settings()
    bypass = getattr(settings, "AUTH_BYPASS", "false").lower() == "true"
    allow = getattr(settings, "AUTH_BYPASS_ALLOW", "false").lower() == "true"
    return bypass and allow


async def _resolve_session_user(
    session_token: str | None,
    db: AsyncSession,
) -> tuple[User | None, str | None]:
    """Returns (user, auth_level) or (None, None)."""

    if _is_auth_bypass_active():
        result = await db.execute(select(User).where(User.is_admin == True))
        user = result.scalars().first()
        if user:
            return user, "password"
        return None, None

    if session_token:
        token_hash = hash_session_token(session_token)
        result = await db.execute(
            select(AdminSession).where(
                AdminSession.token_hash == token_hash,
                AdminSession.revoked == False,
            )
        )
        sess = result.scalar_one_or_none()
        if sess and sess.expires_at > datetime.now(timezone.utc):
            result = await db.execute(select(User).where(User.id == sess.user_id))
            user = result.scalar_one_or_none()
            if user:
                return user, sess.auth_level

    return None, None


async def get_current_user(
    request: Request,
    session_token: str | None = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> User:
    user, _ = await _resolve_session_user(session_token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


async def get_current_admin(
    request: Request,
    session_token: str | None = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> User:
    user, _ = await _resolve_session_user(session_token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user


async def get_passkey_admin(
    request: Request,
    session_token: str | None = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> User:
    user, auth_level = await _resolve_session_user(session_token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    if auth_level != "passkey":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Passkey authentication required for this action",
        )
    return user


async def get_optional_user(
    request: Request,
    session_token: str | None = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    user, _ = await _resolve_session_user(session_token, db)
    return user


async def get_optional_admin(
    request: Request,
    session_token: str | None = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    user, _ = await _resolve_session_user(session_token, db)
    if user and user.is_admin:
        return user
    return None


@router.post("/login")
async def login(
    req: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = generate_session_token()
    token_hash = hash_session_token(token)
    from app.utils.auth import PASSWORD_SESSION_DAYS
    from datetime import timedelta

    sess = AdminSession(
        user_id=user.id,
        token_hash=token_hash,
        auth_level="password",
        expires_at=get_session_expiry("password"),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500],
    )
    db.add(sess)
    await db.flush()

    from app.services.audit_service import record_audit
    await record_audit(
        db,
        action="login",
        entity_type="session",
        entity_id=str(sess.id),
        after={"auth_level": "password", "username": user.username},
        actor_session_id=sess.id,
        auth_level="password",
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500],
    )

    max_age = PASSWORD_SESSION_DAYS * 86400
    response = JSONResponse(
        content={
            "user": {"id": str(user.id), "username": user.username, "is_admin": user.is_admin, "auth_level": "password"},
            "message": "Login successful",
        }
    )
    _set_session_cookie(response, token, request, max_age)
    return response


@router.post("/login-passkey")
async def login_passkey(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    from app.models.session import PasskeyCredential
    from app.services.passkey_service import verify_authentication

    body = await request.json()
    assertion = body.get("assertion")
    if not assertion:
        raise HTTPException(status_code=400, detail="Missing assertion")

    result = await db.execute(select(PasskeyCredential))
    cred = result.scalar_one_or_none()
    if not cred:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No passkey registered")

    ok, new_sign_count = verify_authentication(
        assertion,
        stored_credential_id=cred.credential_id,
        stored_public_key=cred.public_key,
        stored_sign_count=cred.sign_count,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passkey verification failed")

    cred.sign_count = new_sign_count
    cred.last_used_at = datetime.now(timezone.utc)
    db.add(cred)

    result = await db.execute(select(User).where(User.is_admin == True))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No admin user found")

    token = generate_session_token()
    token_hash = hash_session_token(token)

    sess = AdminSession(
        user_id=user.id,
        token_hash=token_hash,
        auth_level="passkey",
        expires_at=get_session_expiry("passkey"),
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500],
    )
    db.add(sess)
    await db.flush()

    from app.services.audit_service import record_audit
    await record_audit(
        db,
        action="login",
        entity_type="session",
        entity_id=str(sess.id),
        after={"auth_level": "passkey", "username": user.username},
        actor_session_id=sess.id,
        auth_level="passkey",
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", "")[:500],
    )

    max_age = PASSKEY_SESSION_DAYS * 86400
    response = JSONResponse(
        content={
            "user": {"id": str(user.id), "username": user.username, "is_admin": user.is_admin, "auth_level": "passkey"},
            "message": "Login successful",
        }
    )
    _set_session_cookie(response, token, request, max_age)
    return response


@router.get("/passkey/auth-options")
async def passkey_auth_options():
    from app.services.passkey_service import generate_authentication_options
    return generate_authentication_options()


@router.get("/passkey/reg-options")
async def passkey_reg_options():
    from app.services.passkey_service import generate_registration_options
    return generate_registration_options()


def _require_operator_key(x_operator_registration_key: str | None) -> None:
    settings = get_settings()
    configured_key = settings.OPERATOR_REGISTRATION_KEY
    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator registration is not configured",
        )
    if not x_operator_registration_key or x_operator_registration_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid operator registration key",
        )


@router.post("/passkey/operator/validate-key")
async def operator_validate_key(
    x_operator_registration_key: str | None = Header(None, alias="X-Operator-Registration-Key"),
):
    _require_operator_key(x_operator_registration_key)
    return {"valid": True}


@router.post("/passkey/operator/reg-options")
async def operator_passkey_reg_options(
    req: OperatorRegOptionsRequest,
    x_operator_registration_key: str | None = Header(None, alias="X-Operator-Registration-Key"),
):
    _require_operator_key(x_operator_registration_key)

    import secrets as secrets_mod
    from app.services.passkey_service import generate_operator_registration_options

    session_id = secrets_mod.token_hex(16)
    options = generate_operator_registration_options(session_id)
    return {"options": options, "session_id": session_id}


@router.post("/passkey/operator/register", response_model=OperatorRegisterResponse)
async def operator_passkey_register(
    req: OperatorRegisterRequest,
    x_operator_registration_key: str | None = Header(None, alias="X-Operator-Registration-Key"),
    db: AsyncSession = Depends(get_db),
):
    _require_operator_key(x_operator_registration_key)

    from app.services.passkey_service import verify_operator_registration, replace_credential

    settings = get_settings()
    result = verify_operator_registration(
        req.attestation,
        session_id=req.session_id,
        expected_origin=settings.WEBAUTHN_ORIGIN,
        expected_rp_id=settings.WEBAUTHN_RP_ID,
    )
    if not result:
        return OperatorRegisterResponse(
            success=False,
            message="WebAuthn registration verification failed (challenge may have expired or session_id mismatch)",
        )

    try:
        new_cred = await replace_credential(
            db,
            result["credential_id"],
            result["public_key"],
            req.device_name,
        )
        await db.flush()

        from app.services.audit_service import record_audit
        await record_audit(
            db,
            action="operator_passkey_register",
            entity_type="passkey_credential",
            entity_id=str(new_cred.id),
            after={"device_name": req.device_name, "path": "operator"},
        )

        await db.commit()

        logger.info(f"Operator passkey registered: device={req.device_name}, credential_id={new_cred.credential_id[:16]}...")
        return OperatorRegisterResponse(
            success=True,
            device_name=req.device_name,
            message="Passkey registered and replaced successfully",
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Operator passkey registration failed: {e}")
        return OperatorRegisterResponse(
            success=False,
            message=f"Registration failed: {str(e)}",
        )


@router.get("/passkey/status")
async def passkey_status(db: AsyncSession = Depends(get_db)):
    from app.models.session import PasskeyCredential
    result = await db.execute(select(PasskeyCredential).limit(1))
    cred = result.scalar_one_or_none()
    return {"registered": cred is not None}


@router.post("/logout")
async def logout(
    request: Request,
    session_token: str | None = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
):
    if session_token:
        token_hash = hash_session_token(session_token)
        result = await db.execute(
            select(AdminSession).where(AdminSession.token_hash == token_hash)
        )
        sess = result.scalar_one_or_none()
        if sess:
            sess.revoked = True
            db.add(sess)

            from app.services.audit_service import record_audit
            await record_audit(
                db,
                action="logout",
                entity_type="session",
                entity_id=str(sess.id),
                actor_session_id=sess.id,
                auth_level=sess.auth_level,
                ip=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent", "")[:500],
            )

    response = JSONResponse(content={"message": "Logged out"})
    _clear_session_cookie(response)
    return response


@router.post("/register", response_model=UserOut)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    x_registration_key: str | None = Header(None, alias="X-Registration-Key"),
):
    settings = get_settings()

    enable_reg = settings.ENABLE_REGISTRATION
    if settings.ENV == "production" and not settings.REGISTRATION_KEY:
        enable_reg = False

    if not enable_reg:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled"
        )

    if settings.REGISTRATION_KEY:
        provided_key = req.registration_key or x_registration_key
        if provided_key != settings.REGISTRATION_KEY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid registration key"
            )

    result = await db.execute(select(User).where(User.username == req.username))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    user = User(username=req.username, password_hash=hash_password(req.password))
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.get("/me")
async def me(
    request: Request,
    session_token: str | None = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
):
    user, auth_level = await _resolve_session_user(session_token, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return {"id": str(user.id), "username": user.username, "is_admin": user.is_admin, "auth_level": auth_level}


@router.get("/sessions")
async def list_sessions(
    user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AdminSession)
        .where(AdminSession.user_id == user.id)
        .order_by(AdminSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "auth_level": s.auth_level,
            "expires_at": s.expires_at.isoformat(),
            "revoked": s.revoked,
            "ip": s.ip,
            "user_agent": s.user_agent,
            "created_at": s.created_at.isoformat(),
        }
        for s in sessions
    ]


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    import uuid as uuid_mod

    try:
        sid = uuid_mod.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session id")

    result = await db.execute(
        select(AdminSession).where(
            AdminSession.id == sid,
            AdminSession.user_id == user.id,
        )
    )
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    sess.revoked = True
    db.add(sess)
    return {"message": "Session revoked"}


@router.post("/set-password")
async def set_password(
    req: SetPasswordRequest,
    user: User = Depends(get_passkey_admin),
    session_token: str | None = Cookie(None, alias=SESSION_COOKIE_NAME),
    db: AsyncSession = Depends(get_db),
):
    token_hash = hash_session_token(session_token) if session_token else None
    session_id = None
    if token_hash:
        result = await db.execute(
            select(AdminSession).where(AdminSession.token_hash == token_hash)
        )
        sess = result.scalar_one_or_none()
        if sess:
            session_id = sess.id

    result = await db.execute(select(AdminPassword).limit(1))
    admin_pw = result.scalar_one_or_none()
    if admin_pw:
        admin_pw.password_hash = hash_password(req.password)
        admin_pw.updated_by_session_id = session_id
        db.add(admin_pw)
    else:
        admin_pw = AdminPassword(
            username="admin",
            password_hash=hash_password(req.password),
            updated_by_session_id=session_id,
        )
        db.add(admin_pw)

    result = await db.execute(select(User).where(User.is_admin == True))
    admin_user = result.scalars().first()
    if admin_user:
        admin_user.password_hash = hash_password(req.password)
        db.add(admin_user)

    return {"message": "Password updated"}
