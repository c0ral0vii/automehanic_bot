import asyncio
import logging
import pathlib
import time
import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from bot.api.schemas.models import ItemRequest
from bot.database.db_config import (
    get_all_user_counts,
    get_items_db,
    get_item,
    add_or_update_product_to_db,
    delete_product_from_db, update_catalog, get_user_by_days,
)


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
    users = await get_user_by_days()

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

UPLOAD_DIR = pathlib.Path(__file__).parent.parent.parent
PRESENTATIONS_DIR = UPLOAD_DIR / "utils" / "data" / "presentations"
CATALOG_DIR = UPLOAD_DIR / "utils" / "data" / "catalog"


async def upload_presentation_by_file(file: UploadFile = File(...)):
    """Загрузка презентации"""
    
    # Создаем директорию, если она не существует
    PRESENTATIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Проверяем тип файла
    if not file.filename.lower().endswith(('.pdf')):
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только файлы с расширением .pdf"
        )
        
    file_location = PRESENTATIONS_DIR / file.filename
    
    # Если файл существует, удаляем его
    if file_location.exists():
        file_location.unlink()
        
    async with aiofiles.open(file_location, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            await f.write(chunk)
            
    
@router.post("/upload_presentation")
async def upload_presentation(file: UploadFile = File(None)):
    try:
        
        asyncio.create_task(upload_presentation_by_file(file))
        return JSONResponse(content={"success": True, "filename": file.filename})
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")
    except Exception as e:
        logging.error(f"Error uploading presentation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка при загрузке файла: {str(e)}")


@router.delete("/presentations/{file_name}")
async def delete_presentation(file_name: str):
    try:
        file_path = PRESENTATIONS_DIR / file_name

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Presentation not found")

        # Delete the file
        file_path.unlink()
        return JSONResponse(status_code=200, content={"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presentations")
async def get_presentations():
    try:
        data = {
            "items": []  # Use "items" to match the frontend expectation
        }

        for file in PRESENTATIONS_DIR.iterdir():
            if file.is_file():
                data["items"].append({"name": file.name})

        return JSONResponse(data, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload_catalog")
async def upload_catalog(file: UploadFile = File(...)):
    """Обновление каталога"""
    
    if not file.filename.lower().endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="Поддерживаются только файлы с расширением .xlsx"
        )

    try:
        file_location = CATALOG_DIR / "data.xlsx"
        if file_location.exists():
            file_location.unlink()

        async with aiofiles.open(file_location, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                await f.write(chunk)

        return JSONResponse(content={"success": True, "filename": file.filename}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog/refresh")
async def refresh_catalog():
    try:
        await update_catalog()

        return JSONResponse(content={"success": True}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))