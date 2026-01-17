from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.db.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

Local_Session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
