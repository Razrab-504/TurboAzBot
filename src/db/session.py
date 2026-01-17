from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.db.config import settings
from urllib.parse import unquote

engine = create_async_engine(
    (settings.DATABASE_URL),
    echo=True,
    connect_args={"statement_cache_size": 0, "server_settings": {"sslmode": "require"}},
)

Local_Session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)
