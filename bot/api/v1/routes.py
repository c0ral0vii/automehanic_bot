import logging

from fastapi import APIRouter, HTTPException, UploadFile, File
import shutil
from fastapi.responses import JSONResponse

from api.schemas.models import ItemRequest
from database.db_config import (
    get_all_user_counts,
    get_user_by_hours,
    get_items_db,
    get_item,
    add_or_update_product_to_db,
    delete_product_from_db,
)

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
        "system_load": f"-",
    }

    return JSONResponse(content=data)


@router.get("/analytics/activity")
async def get_activity_data():
    """Получение данных активности"""
    users = await get_user_by_hours()

    return JSONResponse(
        content={
            "labels": users.get("labels", []),
            "values": users.get("values", []),
        }
    )


@router.get("/analytics/users")
async def get_user_data():
    """Получение данных количества пользователей"""
    all_users = await get_all_user_counts()

    data = {
        "values": [
            all_users.get("authorized_users", 1),
            all_users.get("non_authorized", 0),
        ]  # auth, non-auth
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

    data = {
        "items": items[skip : skip + limit],
        "total": len(items),
        "page": skip // limit + 1 if search == "" else 1,
        "total_pages": (len(items) + limit - 1) // limit,
    }

    return JSONResponse(content=data)


@router.get("/items/{item_id}/info")
async def get_item_info(item_id: int):
    """Получение информации о товаре"""

    item = await get_item(item_id)
    data = {
        "name": item.name,
        "article": item.article_number,
        "cross_number": item.cross_numbers,
        "amount": item.amount,
        "default_price": item.default_price,
        "first_price": item.first_lvl_price,
        "second_lvl_price": item.second_lvl_price,
        "third_lvl_price": item.third_lvl_price,
        "fourth_lvl_price": item.fourth_lvl_price,
        "brand": item.brand,
        "product_group": item.product_group,
        "part_type": item.part_type,
        "photo_url_1": item.photo_url_1,
        "photo_url_2": item.photo_url_2,
        "photo_url_3": item.photo_url_3,
        "photo_url_4": item.photo_url_4,
        "applicability_brands": item.applicability_brands,
        "applicable_tech": item.applicable_tech,
        "weight_kg": item.weight_kg,
        "length_m": item.length_m,
        "inner_diameter_mm": item.inner_diameter_mm,
        "outer_diameter_mm": item.outer_diameter_mm,
        "thread_diameter_mm": item.thread_diameter_mm,
        "width_m": item.width_m,
        "height_m": item.height_m,
    }

    return JSONResponse(content=data)


@router.put("/items/{item_id}/change")
async def change_item_info(item_id: int, item: ItemRequest):
    """Изменение товара"""

    try:
        await add_or_update_product_to_db(product_data=item.model_dump())
        return JSONResponse(
            content={
                "status": 200,
                "change": True,
                "item_id": item_id,
            },
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": 500,
                "change": False,
                "error": str(e),
            },
            status_code=500,
        )


@router.delete("/items/{item_id}/delete")
async def delete_item(item_id: int):
    """Удаление айтема из каталога"""

    await delete_product_from_db(item_id)
    return JSONResponse(
        content={
            "status": 200,
            "delete": True,
            "item_id": item_id,
        }
    )


# @router.post("/upload_presentation/")
# async def upload_presentation(file: UploadFile = File()):
#     try:
#         # Save the uploaded file to a directory on the server
#         file_location = f"uploaded_files/{file.filename}"
#         with open(file_location, "wb") as f:
#             shutil.copyfileobj(file.file, f)
#
#         return JSONResponse(content={"success": True, "filename": file.filename})
#     except Exception as e:
#         return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)
