from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.note import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.utils.auth import create_access_token, decode_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    settings = get_settings()

    # AUTH_BYPASS=true (default): auto-create/return admin, skip JWT.
    # AUTH_BYPASS=false: real JWT auth.
    # To switch to real auth:
    #   1. Register via POST /api/auth/register (creates non-admin user)
    #   2. DB: UPDATE users SET is_admin=true WHERE username='<your_user>';
    #   3. Set AUTH_BYPASS=false in .env
    #   4. Restart backend
    if getattr(settings, "AUTH_BYPASS", "true").lower() == "true":
        result = await db.execute(select(User))
        user = result.scalars().first()
        if user is None:
            user = User(username="admin", password_hash="disabled", is_admin=True)
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            if not user.is_admin:
                user.is_admin = True
                db.add(user)
                await db.commit()
        return user

    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    settings = get_settings()
    if getattr(settings, "AUTH_BYPASS", "true").lower() == "true":
        return user
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    settings = get_settings()
    if getattr(settings, "AUTH_BYPASS", "true").lower() == "true":
        return await get_current_user(credentials, db)
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.post("/register", response_model=UserOut)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
    x_registration_key: str | None = Header(None, alias="X-Registration-Key"),
):
    settings = get_settings()

    # 1. 判定注册开关（如果在生产环境且没有配置 REGISTRATION_KEY，默认强行关闭）
    enable_reg = settings.ENABLE_REGISTRATION
    if settings.ENV == "production" and not settings.REGISTRATION_KEY:
        enable_reg = False

    if not enable_reg:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is disabled"
        )

    # 2. 校验注册秘钥
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


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user
