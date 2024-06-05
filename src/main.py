from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.pages.router import router as pages_router
from src.chat.router import router as chat_router

app = FastAPI(
    title="chat"
)

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = (
    pages_router,
    chat_router,
)

[app.include_router(router) for router in routers]
