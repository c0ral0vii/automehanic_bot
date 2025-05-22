import random

from sqlalchemy import or_, select, func, extract
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime, timedelta
from typing import AsyncGenerator, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from .models import *
import sys

sys.path.append("/app/bot/")
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
from typing import List
from utils.catalog_parser import add_products_from_excel

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
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


async def get_item(item_id: int):
    async with async_session() as session:
        stmt = select(Product).where(Product.id == item_id)
        result = await session.execute(stmt)
        item = result.scalar_one_or_none()

        if not item:
            return {"text": "Не найдено", "error": ""}

        return item


async def get_price_for_user(user_id: int, article_or_cross: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            existing_user = result.scalars().first()

            product_result = await session.execute(
                select(Product).where(
                    or_(
                        Product.article_number == article_or_cross,
                        Product.cross_numbers.ilike(f"%{article_or_cross}%"),
                    )
                )
            )
            product = product_result.scalar_one_or_none()

            if product is None:
                return None

            if existing_user is None or existing_user.role == UserRole.UNDEFINED:
                return product.default_price

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

            return None


async def add_user(
    user_id: int, name: str, surname: str, organization_name: str, phone_number: str
):
    async with async_session() as session:
        async with session.begin():
            new_user = User(
                user_id=user_id,
                name=name,
                surname = surname,
                organization_name = organization_name,
                phone_number = phone_number
            )

            session.add(new_user)
            await session.commit()
            return True


async def get_items_db(find: str = "") -> List[Dict[str, Any]]:
    async with async_session() as session:
        stmt_products = select(
            Product.id,
            Product.article_number,
            Product.cross_numbers,
            Product.name,
            Product.amount,
        )

        if find != "":
            stmt = stmt_products.where(
                or_(
                    Product.article_number.ilike(f"%{find}%"),
                    Product.cross_numbers.ilike(f"%{find}%"),
                    Product.name.ilike(f"%{find}%"),
                )
            )
        else:
            stmt = select(
                Product.id,
                Product.article_number,
                Product.cross_numbers,
                Product.name,
                Product.amount,
            ).order_by(Product.id.asc())

        result_products = await session.execute(stmt)

        products = [
            {
                "id": row.id,
                "article": row.article_number,
                "cross_article": row.cross_numbers,
                "name": row.name,
                "count": row.amount,
            }
            for row in result_products
        ]

        return products


async def add_start_user(user_id: int):
    async with async_session() as session:
        async with session.begin():
            try:
                result = await session.execute(
                    select(User).where(User.user_id == user_id)
                )
                existing_user = result.scalars().first()

                if existing_user:
                    return False

                new_user = User(
                    user_id=user_id,
                )
                session.add(new_user)
                await session.commit()
                return True
            except IntegrityError:
                return False
            except Exception:
                return False


async def get_product_by_article_or_cross_number(article_or_cross: str):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Product).where(
                    or_(
                        Product.article_number == article_or_cross,
                        Product.cross_numbers.ilike(f"%{article_or_cross}%"),
                    )
                )
            )
            product = result.scalar_one_or_none()
            return product


async def add_product():
    async with async_session() as session:
        async with session.begin():
            try:
                async for product in add_products_from_excel():

                    result = await session.execute(
                        select(Product).where(
                            Product.article_number == product.get("article_number")
                        )
                    )
                    existing_product = result.scalar_one_or_none()

                    if existing_product:
                        continue

                    new_product = Product(
                        article_number=product.get("article_number"),
                        name=product.get("name"),
                        amount=product.get("amount"),
                        default_price=product.get("default_price"),
                        first_lvl_price=product.get("first_lvl_price"),
                        second_lvl_price=product.get("second_lvl_price"),
                        third_lvl_price=product.get("third_lvl_price"),
                        fourth_lvl_price=product.get("fourth_lvl_price"),
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


async def get_all_user_counts() -> dict:
    async with async_session() as session:
        stmt_total = select(func.count(User.id))
        result_total = await session.execute(stmt_total)
        total_users = result_total.scalar()

        stmt_updated_today = select(func.count(User.id)).where(
            func.date(User.updated) == date.today()
        )
        result_updated_today = await session.execute(stmt_updated_today)
        updated_today = result_updated_today.scalar()

        stmt_authorized = select(func.count(User.id)).where(
            User.role != UserRole.UNDEFINED
        )
        result_authorized = await session.execute(stmt_authorized)
        authorized_users = result_authorized.scalar()

        stmt_non_authorized = select(func.count(User.id)).where(
            User.role != UserRole.USER,
        )
        result_non_authorized = await session.execute(stmt_non_authorized)
        non_authorized = result_non_authorized.scalar()

        return {
            "total_users": total_users,
            "updated_today": updated_today,
            "authorized_users": authorized_users,
            "non_authorized": non_authorized,
        }


async def get_user_by_days():
    async with async_session() as session:
        # Calculate the date range for the last 7 days
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=6)  # Last 7 days including today

        # Generate a list of dates for the last 7 days
        date_range = [start_date + timedelta(days=i) for i in range(7)]

        # Query the database for user counts per day
        stmt_users_by_day = (
            select(func.date(User.updated).label("date"), func.count(User.id))
            .where(User.updated >= start_date)
            .group_by(func.date(User.updated))
            .order_by(func.date(User.updated))
        )

        result_users_by_day = await session.execute(stmt_users_by_day)
        users_by_day = result_users_by_day.fetchall()

        # Create a dictionary to store the results
        user_counts = {row[0]: row[1] for row in users_by_day}

        # Fill in missing days with 0
        labels = []
        values = []
        for date in date_range:
            date_str = date.strftime("%Y-%m-%d")  # Format date as string
            labels.append(date_str)
            values.append(user_counts.get(date_str, 0))

        return {"labels": labels, "values": values}


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
            result = await session.execute(select(User).where(User.user_id == user_id))
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
            result = await session.execute(
                select(User).where(User.user_id.in_(user_ids))
            )
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

            if not user or user.role == UserRole.UNDEFINED:
                return False
            
            return True


async def my_profile(user_id: int) -> dict | None:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.user_id == user_id))
            user = result.scalars().first()

            if not user:
                return

            return {
                "name": user.name,
                "surname": user.surname,
                "phone": user.phone_number,
                "organization": user.organization_name,
                "role": "Авторизован",
            }


async def delete_product_from_db(item_id: int):
    """Удаление товара"""

    async with async_session() as session:
        stmt = select(Product).where(Product.id == item_id)
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            return

        await session.delete(product)
        await session.commit()


async def add_or_update_product_to_db(
        product_data: dict,
        session: AsyncSession = None
        ):
    not_session = None
    if not session:
        not_session = True
        async with async_session() as session:
            stmt = select(Product).where(Product.article_number == product_data["article_number"])
            result = await session.execute(stmt)
    else:
        stmt = select(Product).where(Product.article_number == product_data["article_number"])
        result = await session.execute(stmt)

    existing_product = result.scalars().first()

    if existing_product:
        existing_product.name = product_data["name"]
        existing_product.amount = product_data["amount"]
        existing_product.default_price = product_data["default_price"]
        existing_product.first_lvl_price = product_data["first_lvl_price"]
        existing_product.second_lvl_price = product_data["second_lvl_price"]
        existing_product.third_lvl_price = product_data["third_lvl_price"]
        existing_product.fourth_lvl_price = product_data["fourth_lvl_price"]
        existing_product.brand = product_data["brand"]
        existing_product.product_group = product_data["product_group"]
        existing_product.part_type = product_data["part_type"]
        existing_product.photo_url_1 = product_data["photo_url_1"]
        existing_product.photo_url_2 = product_data["photo_url_2"]
        existing_product.photo_url_3 = product_data["photo_url_3"]
        existing_product.photo_url_4 = product_data["photo_url_4"]
        existing_product.cross_numbers = product_data["cross_numbers"]
        existing_product.applicability_brands = product_data["applicability_brands"]
        existing_product.applicable_tech = product_data["applicable_tech"]
        existing_product.weight_kg = product_data["weight_kg"]
        existing_product.length_m = product_data["length_m"]
        existing_product.inner_diameter_mm = product_data["inner_diameter_mm"]
        existing_product.outer_diameter_mm = product_data["outer_diameter_mm"]
        existing_product.thread_diameter_mm = product_data["thread_diameter_mm"]
        existing_product.width_m = product_data["width_m"]
        existing_product.height_m = product_data["height_m"]
        session.add(existing_product)
        if not_session:
            await session.commit()
    else:
        new_product = Product(
            article_number=product_data["article_number"],
            name=product_data["name"],
            amount=product_data["amount"],
            default_price=product_data["default_price"],
            first_lvl_price=product_data["first_lvl_price"],
            second_lvl_price=product_data["second_lvl_price"],
            third_lvl_price=product_data["third_lvl_price"],
            fourth_lvl_price=product_data["fourth_lvl_price"],
            brand=product_data["brand"],
            product_group=product_data["product_group"],
            part_type=product_data["part_type"],
            photo_url_1=product_data["photo_url_1"],
            photo_url_2=product_data["photo_url_2"],
            photo_url_3=product_data["photo_url_3"],
            photo_url_4=product_data["photo_url_4"],
            cross_numbers=product_data["cross_numbers"],
            applicability_brands=product_data["applicability_brands"],
            applicable_tech=product_data["applicable_tech"],
            weight_kg=product_data["weight_kg"],
            length_m=product_data["length_m"],
            inner_diameter_mm=product_data["inner_diameter_mm"],
            outer_diameter_mm=product_data["outer_diameter_mm"],
            thread_diameter_mm=product_data["thread_diameter_mm"],
            width_m=product_data["width_m"],
            height_m=product_data["height_m"],
        )
        session.add(new_product)


async def update_amount(article: str, amount: str | int) -> None:
    async with async_session() as session:
        stmt = select(Product).where(Product.article_number == article)
        result = await session.execute(stmt)
        product = result.scalar_one_or_none()

        if not product:
            return

        product.amount = str(amount)
        session.add(product)
        await session.commit()

async def update_catalog():
    async with async_session() as session:
        async with session.begin():
            async for product_data in add_products_from_excel():
                await add_or_update_product_to_db(session=session, product_data=product_data)

        await session.commit()
