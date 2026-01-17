import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import BigInteger, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base

if TYPE_CHECKING:
    from .searchfilter import SearchFilter


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(128))
    full_name: Mapped[str | None] = mapped_column(String(128))

    role: Mapped[str] = mapped_column(String(10), default="user")
    subscription: Mapped[bool] = mapped_column(Boolean, default=False)
    language: Mapped[str] = mapped_column(String(2), default="ru")

    expiry_date: Mapped[datetime.datetime | None] = mapped_column(DateTime)

    is_trial_used: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    filters: Mapped[List["SearchFilter"]] = relationship("SearchFilter", back_populates="user", cascade="all, delete-orphan")
