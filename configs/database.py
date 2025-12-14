from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, DeclarativeBase

from configs.env import settings_config

settings = settings_config()

engine = create_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    # Base hiện tại chưa cần thêm logic
    # nhưng bắt buộc phải tồn tại như một lớp con
    # để SQLAlchemy sử dụng
    pass