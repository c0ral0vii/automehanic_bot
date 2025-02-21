from pydantic import BaseModel
from typing import Optional


class ItemRequest(BaseModel):
    article_number: str
    cross_numbers: str
    name: str
    amount: str
    default_price: str | None = None
    first_lvl_price: str | None = None
    second_lvl_price: str | None = None
    third_lvl_price: str | None = None
    fourth_lvl_price: str | None = None

    brand: str | None = None
    product_group: str | None = None
    part_type: str | None = None

    photo_url_1: str | None = None
    photo_url_2: str | None = None
    photo_url_3: str | None = None
    photo_url_4: str | None = None

    applicability_brands: str | None = None
    applicable_tech: str | None = None
    weight_kg: str | None = None
    length_m: str | None = None
    inner_diameter_mm: str | None = None
    outer_diameter_mm: str | None = None
    thread_diameter_mm: str | None = None
    width_m: str | None = None
    height_m: str | None = None
