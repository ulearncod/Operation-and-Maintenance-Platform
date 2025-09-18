from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    require_roles,
    get_user_roles,
)
from app.models.auth import User, Role, UserRole
from app.core.config import settings

router = APIRouter()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user.username, "uid": user.id}, expires_delta=access_token_expires)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    roles = get_user_roles(db, current_user.id)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "roles": roles,
    }


@router.get("/admin/ping")
def admin_ping(_: User = Depends(require_roles("admin"))):
    return {"message": "pong", "role": "admin"}


class CreateUserBody(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None


@router.post("/users", status_code=201)
def create_user(body: CreateUserBody, _: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    # 检查重名/重复邮箱
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")

    # 创建用户
    from app.core.security import get_password_hash

    user = User(
        username=body.username,
        email=body.email,
        password_hash=get_password_hash(body.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 赋予默认角色 user
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        db.add(UserRole(user_id=user.id, role_id=user_role.id))
        db.commit()

    return {"id": user.id, "username": user.username, "email": user.email}


@router.post("/register", status_code=201)
def register(body: CreateUserBody, db: Session = Depends(get_db)):
    """公开注册接口：创建一个普通用户账号。"""
    # 检查重名/重复邮箱
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if body.email and db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="邮箱已存在")

    from app.core.security import get_password_hash

    user = User(
        username=body.username,
        email=body.email,
        password_hash=get_password_hash(body.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # 赋予默认角色 user
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        db.add(UserRole(user_id=user.id, role_id=user_role.id))
        db.commit()

    return {"id": user.id, "username": user.username, "email": user.email}
