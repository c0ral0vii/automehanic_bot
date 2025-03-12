import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from bot.api.schemas.models import UserLoginSchema
from bot.config import ADMIN_API_TOKEN, ADMIN_USER, ADMIN_PASS
from authx import AuthX, AuthXConfig

router = APIRouter()
config = AuthXConfig()
config.JWT_SECRET_KEY = ADMIN_API_TOKEN
config.JWT_ACCESS_COOKIE_NAME = "JWT_TOKEN"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)


@router.post("/login")
async def login(creds: UserLoginSchema):
    if creds.username == ADMIN_USER and creds.password == ADMIN_PASS:
        token = security.create_access_token(uid=str(uuid.uuid4()))

        print("✅ Устанавливаем куку my_access_token")
        data = JSONResponse({"access_token": token})
        data.set_cookie(key=config.JWT_ACCESS_COOKIE_NAME, value=token)
        return data

    raise HTTPException(status_code=401, detail="Invalid username or password")
