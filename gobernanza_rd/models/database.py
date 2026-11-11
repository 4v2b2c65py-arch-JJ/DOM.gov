# Database Configuration and Base Models
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Index, UniqueConstraint, Enum as SQLEnum, Numeric, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, INET, JSONB, TSVECTOR
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr
import uuid
from datetime import datetime
from typing import Optional
from config.settings import get_settings

settings = get_settings()

# Async Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all models with common fields"""
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)


# Mixin for soft delete
class SoftDeleteMixin:
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = func.now()


# Mixin for audit trail
class AuditMixin:
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)


# Database dependency
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()