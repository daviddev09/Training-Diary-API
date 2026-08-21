from fastapi import Request, status
from fastapi.responses import JSONResponse


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "fail",
            "error": {
                "message": "Непредвиденная внутренняя ошибка сервера",
                "exc_type": "InternalServerError",
            },
        },
    )
