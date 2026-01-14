from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db import init_db
from routers.auth import router as auth_router
from routers.gmail import router as gmail_router
from routers.services import router as services_router
from routers.requests import router as requests_router
from settings import settings
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="ZeroFootprint API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
def root():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(gmail_router)
app.include_router(services_router)
app.include_router(requests_router)
