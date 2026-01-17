import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base



class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    
    title: Mapped[str] = mapped_column(String(256))
    price: Mapped[str] = mapped_column(String(64))
    url: Mapped[str] = mapped_column(String(512))
    city: Mapped[str | None] = mapped_column(String(128))
    published_at: Mapped[str | None] = mapped_column(String(128))

    found_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    last_price: Mapped[str | None] = mapped_column(String(64))
