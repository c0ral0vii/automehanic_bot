from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .models import *
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from typing import List
from utils.catalog_parser import add_products_from_excel

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False,
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


async def check_user_role(user_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        existing_user = result.scalars().first()
        return existing_user.role if existing_user else None


async def get_price_for_user(user_id: int, article_number: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            existing_user = result.scalars().first()

            if existing_user is None or existing_user.role == UserRole.UNDEFINED:
                return PriceLevel.DEFAULT.value

            product_result = await session.execute(
                select(Product).where(Product.article_number == article_number)
            )
            product = product_result.scalar_one_or_none()

            if product is None:
                return None

            return existing_user.price_level.value

            if existing_user.price_level == PriceLevel.DEFAULT:
                return product.default_price

            if existing_user.price_level == PriceLevel.FIRST:
                return product.first_lvl_price

            if existing_user.price_level == PriceLevel.SECOND:
                return product.second_lvl_price

            if existing_user.price_level == PriceLevel.THIRD:
                return product.third_lvl_price

            if existing_user.price_level == PriceLevel.FOURTH:
                return product.fourth_lvl_price



async def add_user(user_id: int, name: str, surname: str, organization_name: str, phone_number: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            existing_user = result.scalars().first()

            if existing_user:
                return False

            new_user = User(
                user_id=user_id,
                name=name,
                surname=surname,
                organization_name=organization_name,
                phone_number=phone_number
            )
            session.add(new_user)
            await session.commit()
            return True

async def get_product(article: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Product).where(Product.article_number == article)
            )
            product = result.scalar_one_or_none()
            return product

async def add_product():
    async with async_session() as session:
        async with session.begin():
            try:
                async for product in add_products_from_excel():
                        
                    result = await session.execute(
                        select(Product).where(Product.article_number == product.get('article_number'))
                    )
                    existing_product = result.scalar_one_or_none()

                    if existing_product:
                        continue

                    new_product = Product(
                        article_number=product.get('article_number'),
                        name=product.get('name'),
                        amount=product.get('amount'),
                        default_price=product.get('default_price'),
                        first_lvl_price=product.get('first_lvl_price'),
                        second_lvl_price=product.get('second_lvl_price'),
                        third_lvl_price=product.get('third_lvl_price'),
                        fourth_lvl_price=product.get('fourth_lvl_price')
                    )
                    session.add(new_product)
                await session.commit()
            except IntegrityError:
                await session.rollback()
                return f"Ошибка: не удалось добавить продукт. Возможно, артикул уже существует."

async def get_all_users() -> List[User]:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User))
            users = result.scalars().all()
            return users

async def get_user(user_id: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()
            return user

async def get_users_with_role_undefined() -> List[User]:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.role == UserRole.UNDEFINED)
            )
            users = result.scalars().all()
            return users

async def get_users_with_role_cancelled() -> List[User]:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.role == UserRole.CANCELLED)
            )
            users = result.scalars().all()
            return users

async def get_users_with_role_user() -> List[User]:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.role == UserRole.USER)
            )
            users = result.scalars().all()  # Get users with role 'user'
            return users

async def update_user_role(user_id: int, new_role: UserRole):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                return f"Пользователь с ID {user_id} не найден."

            user.role = new_role
            await session.commit()
            return f"Роль пользователя {user.name} {user.surname} успешно обновлена на {new_role.value}."

async def update_price_for_user(user_id: int, new_price_level: PriceLevel):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return f"Пользователь с ID {user_id} не найден."

            user.price_level = new_price_level
            await session.commit()
            return f"Уровень цен для пользователя {user.name} {user.surname} успешно изменён на {new_price_level.value}."

async def update_price_for_group(user_ids: List[int], new_price_level: PriceLevel):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id.in_(user_ids)))
            users = result.scalars().all()

            if not users:
                return "Пользователи с указанными ID не найдены."

            for user in users:
                user.price_level = new_price_level

            await session.commit()
            return f"Уровень цен для пользователей с ID {', '.join(map(str, user_ids))} успешно изменён на {new_price_level.value}."

async def update_price_for_category(category: UserRole, new_price_level: PriceLevel):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.role == category))
            users = result.scalars().all()

            if not users:
                return f"Пользователи с категорией {category.value} не найдены."

            for user in users:
                user.price_level = new_price_level

            await session.commit()
            return f"Уровень цен для всех пользователей с категорией {category.value} успешно изменён на {new_price_level.value}."


async def update_price_for_all_users(new_price_level: PriceLevel):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User))
            users = result.scalars().all()

            if not users:
                return "Пользователи не найдены."

            for user in users:
                user.price_level = new_price_level

            await session.commit()
            return f"Уровень цен для всех пользователей успешно изменён на {new_price_level.value}."

async def update_user_price_level(user_id: int, new_price_level: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return False

            user.price_level = new_price_level
            await session.commit()
            return True
        

async def check_auth(user_id: int) -> bool:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return False
            return True
        

async def my_profile(user_id: int) -> tuple:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalars().first()

            if not user:
                return

            return {
                'name': user.name,
                'surname': user.surname,
                'phone': user.phone_number,
                'organization': user.organization_name,
                'role': 'Авторизован',
            }