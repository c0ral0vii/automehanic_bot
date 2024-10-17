from sqlalchemy import select
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .models import *
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_async_engine(DATABASE_URL, echo=True)


async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def add_user(user_id: int, name: str, surname: str, organization_name:str, phone_number: str):
    async with async_session() as session:
        async with session.begin():
            new_user = User(
            user_id=user_id,
            name=name,
            surname=surname,
            organization_name=organization_name,
            phone_number=phone_number
        )
            session.add(new_user)
            await session.commit()

async def get_product(article: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Product).where(Product.article_number == article)
            )
            product = result.scalar_one_or_none()
            return product

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

async def add_product(article: str, name: str, amount: int, price: float):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Product).where(Product.article_number == article)
            )
            existing_product = result.scalar_one_or_none()

            if existing_product:
                return f"Продукт с артикулом {article} уже существует."

            new_product = Product(
                article_number=article,
                name=name,
                amount=amount,
                price=price
            )

            try:
                session.add(new_product)
                await session.commit()
                return f"Продукт {name} с артикулом {article} успешно добавлен."
            except IntegrityError:
                await session.rollback()
                return f"Ошибка: не удалось добавить продукт {name}. Возможно, артикул уже существует."
