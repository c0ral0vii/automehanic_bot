import aiohttp
from config import API_UID
from database.db_config import get_items_db, update_amount
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создаём обработчик (например, вывод в консоль)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создаём форматтер
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(console_handler)

class UpdateCountService:
    def __init__(self):

        self.BASE_URL = "http://korona-auto.com/"

        self.apiUid = API_UID
        self.dataType = "json"

        self.HEADER = {}
        # self.session = aiohttp.ClientSession()

    async def check_stock(self):
        ids_from_site = await self._find_id_on_site()
        logger.debug(f"ids - {ids_from_site}")
        for key, item in ids_from_site.items():
            try:
                logger.debug(f"Checking {key}, {item}")
                item_id = item.get('id')
                if item_id is None:
                    continue

                url = self.BASE_URL + f"api/product/stock/?id={item_id}&apiUid={self.apiUid}&dataType={self.dataType}"
                response = await self._send_request(url)

                stock = response.get("product", {}).get("stock", {})[0].get("warehouse", {}).get("quantity")

                await update_amount(key, stock)
                logger.info(f"Updated {key}, {stock}")
            except Exception as e:
                continue

    async def _find_id_on_site(self):
        items_from_db = await get_items_db()
        data = {}

        for item in items_from_db:
            try:
                article = item.get("article")
                if not article:
                    continue

                url = self.BASE_URL + f"api/search/?q={article}&apiUid={self.apiUid}&dataType={self.dataType}"
                response = await self._send_request(url)

                id = response.get("product", {})[0].get("id")
                data[article] = {"id": id, "amount": None}

            except Exception as e:
                logger.error(e)
                continue

        return data


    async def _send_request(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if not response.status == 200:
                    return None

                data = await response.text()

                data_json = json.loads(data)
                return data_json


