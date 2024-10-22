from sqlalchemy import Boolean, DateTime, Float, Numeric, String, Text, func, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from enum import Enum
from sqlalchemy import Enum as SqlEnum

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

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
    FOURTH = 'fourth'

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    surname: Mapped[str] = mapped_column(String)
    organization_name: Mapped[str] = mapped_column(String)
    phone_number: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, name="role"), default=UserRole.UNDEFINED)
    price_level: Mapped[PriceLevel] = mapped_column(SqlEnum(PriceLevel, name="price_level"), default=PriceLevel.DEFAULT)


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    cross_numbers: Mapped[list] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[int] = mapped_column(Integer)    
    default_price: Mapped[PriceLevel] = mapped_column(Numeric(10, 2), nullable=True)
    first_lvl_price: Mapped[PriceLevel] = mapped_column(Numeric(10, 2), nullable=True)
    second_lvl_price: Mapped[PriceLevel] = mapped_column(Numeric(10, 2), nullable=True)
    third_lvl_price: Mapped[PriceLevel] = mapped_column(Numeric(10, 2), nullable=True)
    fourth_lvl_price: Mapped[PriceLevel] = mapped_column(Numeric(10, 2), nullable=True)

    def __repr__(self):
        return f"<Product(name='{self.name}', article_number='{self.article_number}')>"