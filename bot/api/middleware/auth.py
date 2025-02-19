from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from config import ADMIN_API_TOKEN


api_key_header = APIKeyHeader(name="X-Admin-Token")


async def verify_admin_token(api_key: str = Security(api_key_header)) -> bool:
    if api_key != ADMIN_API_TOKEN:
        raise HTTPException(
            status_code=403,
            detail="Invalid admin token"
        )
    return True