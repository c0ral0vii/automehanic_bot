import asyncio
import pandas as pd
from bot.database.config import add_product

df = pd.read_excel("data.xlsx", sheet_name='КАТАЛОГ')

df = df[['Исходный номер', 'Наименование', 'Наличие, шт.', 'Розничная цена, руб.']]

async def add_products_from_excel():
    for index, row in df.iterrows():
        article_number = row['Исходный номер']
        name = row['Наименование']
        amount = int(row['Наличие, шт.']) if not pd.isnull(row['Наличие, шт.']) else 0
        price = float(row['Розничная цена, руб.']) if not pd.isnull(row['Розничная цена, руб.']) else 0.0

        await add_product(article_number, name, amount, price)


asyncio.run(add_products_from_excel())
