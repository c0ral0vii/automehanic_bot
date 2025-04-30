from sqlalchemy import Boolean, DateTime, Float, Numeric, String, Text, func, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from enum import Enum
from sqlalchemy import Enum as SqlEnum


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    UNDEFINED = "undefined"
    CANCELLED = "cancelled"


class PriceLevel(str, Enum):
    DEFAULT = "default"
    FIRST = "first"
    SECOND = "second"
    THIRD = "third"
    FOURTH = "fourth"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=True)
    surname: Mapped[str] = mapped_column(String, nullable=True)
    organization_name: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, name="role"), default=UserRole.UNDEFINED
    )
    price_level: Mapped[PriceLevel] = mapped_column(
        SqlEnum(PriceLevel, name="price_level"), default=PriceLevel.DEFAULT
    )


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_number: Mapped[str] = mapped_column(
        unique=True, nullable=False
    )
    cross_numbers: Mapped[list] = mapped_column(String(1000), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[str] = mapped_column(Text)
    default_price: Mapped[str] = mapped_column(Text, nullable=True)
    first_lvl_price: Mapped[str] = mapped_column(Text, nullable=True)
    second_lvl_price: Mapped[str] = mapped_column(Text, nullable=True)
    third_lvl_price: Mapped[str] = mapped_column(Text, nullable=True)
    fourth_lvl_price: Mapped[str] = mapped_column(Text, nullable=True)

    brand: Mapped[str] = mapped_column(nullable=True)  # Бренд
    product_group: Mapped[str] = mapped_column(
        nullable=True
    )  # Товарная группа
    part_type: Mapped[str] = mapped_column(nullable=True)  # Тип запчасти
    photo_url_1: Mapped[str] = mapped_column(
        nullable=True
    )  # Ссылка на фото 1
    photo_url_2: Mapped[str] = mapped_column(
        nullable=True
    )  # Ссылка на фото 2
    photo_url_3: Mapped[str] = mapped_column(
         nullable=True
    )  # Ссылка на фото 3
    photo_url_4: Mapped[str] = mapped_column(
        nullable=True
    )  # Ссылка на фото 3
    applicability_brands: Mapped[str] = mapped_column(
        Text, nullable=True
    )  # Бренды применимости
    applicable_tech: Mapped[str] = mapped_column(
         nullable=True
    )  # Техника применимости
    weight_kg: Mapped[str] = mapped_column( nullable=True)  # Вес, кг
    length_m: Mapped[str] = mapped_column(nullable=True)  # Длина, м
    inner_diameter_mm: Mapped[str] = mapped_column(
        nullable=True
    )  # Внутренний диаметр, мм
    outer_diameter_mm: Mapped[str] = mapped_column(
        nullable=True
    )  # Внешний диаметр, мм
    thread_diameter_mm: Mapped[str] = mapped_column(
        nullable=True
    )  # Диаметр резьбы
    width_m: Mapped[str] = mapped_column(nullable=True)  # Ширина
    height_m: Mapped[str] = mapped_column(nullable=True)  # Высота

    def __repr__(self):
        return f"<Product(name='{self.name}', article_number='{self.article_number}')>"
