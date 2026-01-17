import datetime
from sqlalchemy import BigInteger, String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.db.base import Base


class SentAd(Base):
    __tablename__ = "sent_ads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    ad_id: Mapped[str] = mapped_column(String(64), ForeignKey("advertisements.id"))
    sent_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
