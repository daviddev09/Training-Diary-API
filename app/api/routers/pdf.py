from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_diary_service
from app.models import User
from app.services.diary import DiaryService

router = APIRouter(prefix="/pdf", tags=["PDFs"])


@router.post("/diary/{diary_id}")
async def create_diary_pdf(
    diary_id: int,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> dict[str, str]:
    """
    # Создаёт PDF файл из дневника пользователя и отправляет ссылку для скачивания на почту.
    ## Важно:
    * **Чтобы создать PDF в дневнике должен быть хотя бы 1 пустой день тренировки.**
    * **Пользователь может обращаться в этот эндпоинт раз в час, защищён с помощью Rate Limiting.**
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или дневник не найден.
    * **400 Bad Request** - дневник пуст
    """
    return await service.create_diary_pdf(diary_id, user.uuid, user.email, user.name)
