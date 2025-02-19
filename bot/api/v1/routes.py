import logging
import math
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from api.schemas.models import ItemResponse
from database.db_config import get_all_user_counts, get_user_by_hours, get_items_db

import random

# from schemas.models import UserResponse


router = APIRouter()


@router.get("/stats/overview")
async def get_overview_stats():
    """Получение общей статистики"""

    all_users = await get_all_user_counts()

    data = {
        "total_users": all_users.get("total_users", 0),
        "auth_users": all_users.get("authorized_users", 0),
        "active_today": all_users.get("updated_today", 0),
        "system_status": "HEALTHY",
        "system_load": f"-"
    }

    return JSONResponse(content=data)


@router.get("/analytics/activity")
async def get_activity_data():
    """Получение данных активности"""
    users = await get_user_by_hours()

    return JSONResponse(content={
        "labels": users.get("labels", []),
        "values": users.get("values", []),
    })


@router.get("/analytics/users")
async def get_user_data():
    """Получение данных количества пользователей"""
    all_users = await get_all_user_counts()


    data = {
        "values": [all_users.get("authorized_users", 1), all_users.get("non_authorized", 0)] # auth, non-auth
    }

    return JSONResponse(content=data)


@router.get("/items")
async def get_items(
    skip: int = 0,
    limit: int = 50,
    search: str = "",
):
    """Получение списка пользователей"""

    items = await get_items_db(search)
    logging.debug(items)
    logging.debug(skip, limit)
    data = {
        "items": items[skip:skip + limit],
        "total": len(items),
        "page": skip // limit + 1 if search == "" else 1,
        "total_pages": (len(items) + limit - 1) // limit
    }

    return JSONResponse(content=data)


@router.get("items/{item_id}/info")
async def get_item_info(item_id: int):
    """Получение информации о товаре"""

    ...

@router.put("/items/{item_id}/change")
async def change_item_info(item_id: int):
    """Изменение товара"""

    ...

@router.delete("/items/{item_id}/delete")
async def delete_item(item_id: int):
    """Удаление айтема из каталога"""

    ...