"""
Session-based auth (username/password per role), as chosen over JWT.

Passwords are hashed with PBKDF2-HMAC-SHA256 (stdlib `hashlib`, no extra
native-extension dependency). Sessions are a signed cookie holding the user id,
signed with `itsdangerous` so the server never needs a session table - the
cookie itself can't be forged or tampered with without the app's secret key.
"""
import hashlib
import os
import secrets

from fastapi import Cookie, Depends, HTTPException, status
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, User

SECRET_KEY = os.environ.get("LOANGUARD_SECRET_KEY", "loanguard-ai-dev-secret-change-me")
COOKIE_NAME = "loanguard_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days

serializer = URLSafeTimedSerializer(SECRET_KEY, salt="loanguard-session")


def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return digest.hex(), salt


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    digest, _ = hash_password(password, salt)
    return secrets.compare_digest(digest, password_hash)


def create_session_cookie(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def read_session_cookie(token: str) -> int | None:
    try:
        data = serializer.loads(token, max_age=SESSION_MAX_AGE_SECONDS)
        return data.get("user_id")
    except BadSignature:
        return None


def get_current_user(
    loanguard_session: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not loanguard_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in")
    user_id = read_session_cookie(loanguard_session)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_optional_user(
    loanguard_session: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not loanguard_session:
        return None
    user_id = read_session_cookie(loanguard_session)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_roles(*roles: Role):
    def _dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return user

    return _dependency
