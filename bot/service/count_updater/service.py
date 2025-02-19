import aiohttp
import asyncio
from config import API_UID

class UpdateCountService:
    def __init__(self):

        self.BASE_URL = "http://korona-auto.com/"

        self.apiUid = API_UID
        self.dataType = "json"

        self.HEADER = {}

    async def check_stock(self):
        url = self.BASE_URL + "api/product/stock"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"Статус запроса  - {response.status}, Произошла ошибка.")

                data = await response.json()

                stock = data.get("stock")