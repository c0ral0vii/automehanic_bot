from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.middleware.gzip import GZipMiddleware

import os

from bot.api.v1 import auth

app = FastAPI(
    title="MARSHALL.OFF-HIGHWAY_BOT",
    max_request_size=50 * 1024 * 1024
)

# Добавляем GZip сжатие
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)


static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

from bot.api.v1.routes import router

app.include_router(router, prefix="/api/v1", tags=["Analytic API"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth API"])

# Root endpoint
@app.get(
    "/admin",
    response_class=FileResponse,
    dependencies=[Depends(auth.security.access_token_required)],
)
async def root():
    index_html = static_dir + "/index.html"
    return FileResponse(index_html)


@app.get("/", response_class=FileResponse)
async def auth_page():
    auth_html = static_dir + "/auth.html"
    return FileResponse(auth_html)

