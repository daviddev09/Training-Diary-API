from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routers.admin import router as admin_router
from app.api.routers.auth import router as auth_router
from app.api.routers.diary import router as diary_router
from app.api.routers.exercise import router as exercise_router
from app.api.routers.guest import router as guest_router
from app.api.routers.language import router as lang_router
from app.api.routers.pdf import router as pdf_router
from app.api.routers.user import router as user_router
from app.api.routers.weight import router as weight_router
from app.core.database import init_owner, init_system_exercises
from app.exceptions import AppBaseException
from app.handlers import global_exception_handler
from app.middlewares import EndpointRateLimiterMiddleware, GlobalRateLimiterMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_owner()
    await init_system_exercises()
    yield


origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app = FastAPI(
    lifespan=lifespan,
    title="Training Diary",
    version="1.0.0",
    description="## API для ведения записей о тренировках",
    contact={
        "name": "Daviddev",
        "url": "https://github.com/daviddev09/Training-Diary-API",
        "email": "daviddev09.py@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(GlobalRateLimiterMiddleware)
app.add_middleware(EndpointRateLimiterMiddleware)


@app.exception_handler(AppBaseException)
async def app_exception_handler(
    request: Request, exc: AppBaseException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "fail",
            "exc_type": exc.__class__.__name__,
            "detail": exc.detail,
        },
    )


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(guest_router)
app.include_router(diary_router)
app.include_router(weight_router)
app.include_router(exercise_router)
app.include_router(pdf_router)
app.include_router(lang_router)
app.add_exception_handler(Exception, global_exception_handler)


@app.get("/", tags=["Main"])
async def root() -> dict[str, str]:
    """
    # Возвращает информацию о приложении. Главная страница
    """
    return {"message": "Training-Diary-API", "docs": "/docs"}


@app.get("/health", tags=["Main"])
async def health_check() -> dict[str, str]:
    """
    # Проверка работы API
    """
    return {"status": "ok"}
