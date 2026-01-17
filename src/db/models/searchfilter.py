from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base import Base

if TYPE_CHECKING:
    from .users import User


class SearchFilter(Base):
    __tablename__ = "search_filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    
    query_url: Mapped[str] = mapped_column(String(512))  # Ссылка на Turbo.az с примененными фильтрами
    label: Mapped[str | None] = mapped_column(String(64)) # Название фильтра для пользователя (напр. "Мои Приусы")

    user: Mapped["User"] = relationship("User", back_populates="filters")
