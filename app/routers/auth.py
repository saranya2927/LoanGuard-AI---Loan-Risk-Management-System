from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import (
    COOKIE_NAME,
    create_session_cookie,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models import Role, User
from app.schemas import LoginRequest, RegisterRequest, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

COOKIE_KWARGS = dict(httponly=True, samesite="lax", max_age=60 * 60 * 24 * 7, path="/")


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    password_hash, salt = hash_password(payload.password)
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=password_hash,
        salt=salt,
        role=Role.applicant,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_session_cookie(user.id)
    response.set_cookie(COOKIE_NAME, token, **COOKIE_KWARGS)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.salt, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_session_cookie(user.id)
    response.set_cookie(COOKIE_NAME, token, **COOKIE_KWARGS)
    return user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
