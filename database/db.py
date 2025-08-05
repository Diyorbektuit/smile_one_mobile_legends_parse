from asyncio import current_task
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, async_scoped_session
from contextlib import asynccontextmanager
from security import SECURITY


class DbHelper:
    def __init__(self, url, echo: bool):
        self.engine = create_async_engine(
            url,
            echo=echo,
            pool_size=50,
            max_overflow=100,
            pool_timeout=60,
            pool_recycle=120,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False
        )
        self.scoped_session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        session = self.session_factory()
        try:
            yield session
        finally:
            await session.close()

    @asynccontextmanager
    async def get_scoped_session(self) -> AsyncSession:
        session = self.scoped_session()
        try:
            yield session
        finally:
            await self.scoped_session.close()

    async def session_dependency(self) -> AsyncSession:
        async with self.get_session() as session:
            yield session

    async def scoped_session_dependency(self) -> AsyncSession:
        async with self.get_scoped_session() as session:
            yield session


db_helper = DbHelper(SECURITY.DATABASE_URL, True)

