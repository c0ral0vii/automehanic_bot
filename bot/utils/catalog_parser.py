import pandas as pd

async def add_products_from_excel():
    df = pd.read_excel("./bot/utils/data/catalog/data.xlsx", sheet_name='КАТАЛОГ')
    df = df[['Исходный номер', 'Наименование', 'Наличие, шт.', 'Розничная цена, руб.', 'Уровень цен 1, руб.',
             'Уровень цен 2, руб.', 'Уровень цен 3, руб.', 'Уровень цен 4, руб.', 'Бренд', 'Товарная группа',
             'Тип запчасти', 'Ссылка на фото 1', 'Ссылка на фото 2', 'Ссылка на фото 3', 'Кросс-номера',
             'Бренды применимости', 'Техника применимости', 'Вес, кг.', 'Длина, м.', 'Внутренний диаметр, мм.',
             'Внешний диаметр, мм.', 'Диаметр резьбы']]

    for index, row in df.iterrows():
        article_number = row['Исходный номер']
        name = row['Наименование']
        cross_number = row['Кросс-номера'].split(';') if row['Кросс-номера'] in [';'] else row['Кросс-номера']
        amount = int(row['Наличие, шт.']) if not pd.isnull(row['Наличие, шт.']) else 0
        default_price = float(row['Розничная цена, руб.']) if not pd.isnull(row['Розничная цена, руб.']) else 0.0
        first_lvl_price = float(row['Уровень цен 1, руб.']) if not pd.isnull(row['Уровень цен 1, руб.']) else 0.0
        second_lvl_price = float(row['Уровень цен 2, руб.']) if not pd.isnull(row['Уровень цен 2, руб.']) else 0.0
        third_lvl_price = float(row['Уровень цен 3, руб.']) if not pd.isnull(row['Уровень цен 3, руб.']) else 0.0
        fourth_lvl_price = float(row['Уровень цен 4, руб.']) if not pd.isnull(row['Уровень цен 4, руб.']) else 0.0

        brand = str(row['Бренд']) if not pd.isnull(row['Бренд']) else None
        product_group = str(row['Товарная группа']) if not pd.isnull(row['Товарная группа']) else None
        part_type = str(row['Тип запчасти']) if not pd.isnull(row['Тип запчасти']) else None
        photo_url_1 = str(row['Ссылка на фото 1']) if not pd.isnull(row['Ссылка на фото 1']) else None
        photo_url_2 = str(row['Ссылка на фото 2']) if not pd.isnull(row['Ссылка на фото 2']) else None
        photo_url_3 = str(row['Ссылка на фото 3']) if not pd.isnull(row['Ссылка на фото 3']) else None
        cross_numbers = str(row['Кросс-номера']) if not pd.isnull(row['Кросс-номера']) else None
        applicability_brands = str(row['Бренды применимости']) if not pd.isnull(row['Бренды применимости']) else None
        applicable_tech = str(row['Техника применимости']) if not pd.isnull(row['Техника применимости']) else None
        weight_kg = str(row['Вес, кг.']) if not pd.isnull(row['Вес, кг.']) else None
        length_m = str(row['Длина, м.']) if not pd.isnull(row['Длина, м.']) else None
        inner_diameter_mm = str(row['Внутренний диаметр, мм.']) if not pd.isnull(row['Внутренний диаметр, мм.']) else None
        outer_diameter_mm = str(row['Внешний диаметр, мм.']) if not pd.isnull(row['Внешний диаметр, мм.']) else None
        thread_diameter_mm = str(row['Диаметр резьбы']) if not pd.isnull(row['Диаметр резьбы']) else None

        yield {
            'article_number': article_number,
            'cross_numbers': cross_number,
            'name': name,
            'amount': amount,
            'default_price': default_price,
            'first_lvl_price': first_lvl_price,
            'second_lvl_price': second_lvl_price,
            'third_lvl_price': third_lvl_price,
            'fourth_lvl_price': fourth_lvl_price,
            'brand': brand,
            'product_group': product_group,
            'part_type': part_type,
            'photo_url_1': photo_url_1,
            'photo_url_2': photo_url_2,
            'photo_url_3': photo_url_3,
            'cross_numbers': cross_numbers,
            'applicability_brands': applicability_brands,
            'applicable_tech': applicable_tech,
            'weight_kg': weight_kg,
            'length_m': length_m,
            'inner_diameter_mm': inner_diameter_mm,
            'outer_diameter_mm': outer_diameter_mm,
            'thread_diameter_mm': thread_diameter_mm,
        }


