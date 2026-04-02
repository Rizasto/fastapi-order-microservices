from app.core.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

settings = get_settings()

engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
