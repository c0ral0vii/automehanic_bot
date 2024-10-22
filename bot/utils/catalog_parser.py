import pandas as pd

async def add_products_from_excel():
    df = pd.read_excel("./bot/utils/data/catalog/data.xlsx", sheet_name='КАТАЛОГ') # ./bot/utils/data/catalog/data.xlsx
    df = df[['Исходный номер', 'Наименование', 'Наличие, шт.', 'Розничная цена, руб.', 'Уровень цен 1, руб.',
           'Уровень цен 2, руб.', 'Уровень цен 3, руб.', 'Уровень цен 4, руб.']]
  
    for index, row in df.iterrows():
        article_number = row['Исходный номер']
        name = row['Наименование']
        cross_number = row['Кросс-номера'].split(';')
        amount = int(row['Наличие, шт.']) if not pd.isnull(row['Наличие, шт.']) else 0
        default_price = float(row['Розничная цена, руб.']) if not pd.isnull(row['Розничная цена, руб.']) else 0.0
        first_lvl_price = float(row['Уровень цен 1, руб.']) if not pd.isnull(row['Уровень цен 1, руб.']) else 0.0
        second_lvl_price = float(row['Уровень цен 2, руб.']) if not pd.isnull(row['Уровень цен 2, руб.']) else 0.0
        third_lvl_price = float(row['Уровень цен 3, руб.']) if not pd.isnull(row['Уровень цен 3, руб.']) else 0.0
        fourth_lvl_price = float(row['Уровень цен 4, руб.']) if not pd.isnull(row['Уровень цен 4, руб.']) else 0.0

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
        }

