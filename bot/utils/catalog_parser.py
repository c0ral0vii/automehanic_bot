import asyncio
import pandas as pd
from bot.database.db_config import add_product

# для работы данного скрипта нужно поменять импорт в bot\database\db_config.py
df = pd.read_excel("data.xlsx", sheet_name='КАТАЛОГ')
df = df[['Исходный номер', 'Наименование', 'Наличие, шт.', 'Розничная цена, руб.', 'Уровень цен 1, руб.',
         'Уровень цен 2, руб.', 'Уровень цен 3, руб.', 'Уровень цен 4, руб.']]

async def add_products_from_excel():
    for index, row in df.iterrows():
        article_number = row['Исходный номер']
        name = row['Наименование']
        amount = int(row['Наличие, шт.']) if not pd.isnull(row['Наличие, шт.']) else 0
        default_price = float(row['Розничная цена, руб.']) if not pd.isnull(row['Розничная цена, руб.']) else 0.0
        first_lvl_price = float(row['Уровень цен 1, руб.']) if not pd.isnull(row['Уровень цен 1, руб.']) else None
        second_lvl_price = float(row['Уровень цен 2, руб.']) if not pd.isnull(row['Уровень цен 2, руб.']) else None
        third_lvl_price = float(row['Уровень цен 3, руб.']) if not pd.isnull(row['Уровень цен 3, руб.']) else None
        fourth_lvl_price = float(row['Уровень цен 4, руб.']) if not pd.isnull(row['Уровень цен 4, руб.']) else None

        await add_product(
            article_number=article_number,
            name=name,
            amount=amount,
            default_price=default_price,
            first_lvl_price=first_lvl_price,
            second_lvl_price=second_lvl_price,
            third_lvl_price=third_lvl_price,
            fourth_lvl_price=fourth_lvl_price
        )


asyncio.run(add_products_from_excel())
