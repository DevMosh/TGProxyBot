from datetime import datetime
from sqlalchemy import BigInteger, String, Boolean, DateTime, Float, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True) # <-- Новое поле
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ref_code: Mapped[str | None] = mapped_column(String(50), nullable=True) # Код, по которому пришел юзер

class Channel(Base):
    __tablename__ = 'channels'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True) # ID канала (начинается с -100)
    title: Mapped[str] = mapped_column(String(100)) # Название канала для админки
    url: Mapped[str] = mapped_column(String(100)) # Ссылка для кнопки


class Proxy(Base):
    __tablename__ = 'proxies'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("0"))

    # Новые метрики
    score: Mapped[float] = mapped_column(Float, default=9999.0)  # Чем меньше, тем лучше
    success_checks: Mapped[int] = mapped_column(default=0)  # Успешные пинги
    total_checks: Mapped[int] = mapped_column(default=0)  # Всего пингов

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReferralLink(Base):
    __tablename__ = 'referral_links'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    owner_id: Mapped[int] = mapped_column(BigInteger) # tg_id рекламодателя
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
