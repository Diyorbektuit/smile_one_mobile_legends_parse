import uuid

from sqlalchemy import Column, Integer, String, Boolean, select, update
from sqlalchemy.orm import declarative_base

from database.db import db_helper

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(length=256), index=True)
    username = Column(String(length=256), nullable=True)
    email = Column(String(length=256), nullable=True)
    password = Column(String(length=256), nullable=True)
    telegram_id = Column(Integer, unique=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    x_api_key = Column(String(length=256), nullable=True)

    @classmethod
    async def get_or_create(cls, telegram_id: int, full_name: str, username: str = None) -> None:
        async with db_helper.get_scoped_session() as session:
            result = await session.execute(select(cls).where(cls.telegram_id == telegram_id))
            user = result.scalars().first()
            if user is not None:
                return
            new_user = cls(
                full_name=full_name,
                telegram_id=telegram_id,
                username=username,
                x_api_key=uuid.uuid4(),
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

    @classmethod
    async def get_user_by_telegram_id(cls, telegram_id: int):
        async with db_helper.get_scoped_session() as session:
            result = await session.execute(select(cls).where(cls.telegram_id == telegram_id))
            user = result.scalars().first()
            return user

    @classmethod
    async def update(cls, telegram_id: int, email: str, password: str) -> None:
        async with db_helper.get_scoped_session() as session:
            await session.execute(
                update(cls)
                .where(cls.telegram_id == telegram_id)
                .values(email=email, password=password)
            )
            await session.commit()

    @classmethod
    async def get_all_superusers(cls):
        async with db_helper.get_scoped_session() as session:
            result = await session.execute(select(cls).where(cls.is_superuser == True))
            superusers = result.scalars().all()
            return superusers


