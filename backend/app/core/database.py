"""
数据库连接和初始化
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.DEBUG
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """初始化数据库"""
    # 导入模型以注册到元数据
    from app.models import auth  # noqa: F401

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    # 基础数据：默认角色与管理员账号
    from app.models.auth import Role, User, UserRole
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        # 确保基础角色存在
        for role_name in ["admin", "user"]:
            if not db.query(Role).filter(Role.name == role_name).first():
                db.add(Role(name=role_name))
        db.commit()

        # 创建默认管理员（仅首次）
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=get_password_hash("admin123"),
                is_active=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

            admin_role = db.query(Role).filter(Role.name == "admin").first()
            if admin_role:
                db.add(UserRole(user_id=admin.id, role_id=admin_role.id))
                db.commit()
        print("✅ 数据库初始化完成（角色/管理员已就绪）")
    finally:
        db.close()