from fastapi import APIRouter, Cookie, HTTPException, Response, status

from app.core.languages import LANGUAGES

router = APIRouter(prefix="/language", tags=["Language"])


@router.patch("/set")
async def change_language(lang_code: str, response: Response) -> dict[str, str]:
    """
    # Изменяет язык ответа сервера.
    ## Какие языки есть на данный момент:
    * **ru**: код русского языка
    * **tm**: код туркменского языка
    ## Возможная ошибка:
    * **400 Bad Request** - введённый код языка отсутствует (не поддерживается)
    """
    if lang_code not in LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language: {lang_code} is not supported. Use 'tm' or 'ru'.",
        )

    response.set_cookie(
        key="lang",
        value=lang_code,
        max_age=31536000,
        path="/",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"status": "success", "current_language": lang_code}


@router.get("/translations")
async def get_translations(
    response: Response, lang: str = Cookie(default="ru")
) -> dict[str, str]:
    """
    # Отдаёт нужные фронтенду переводы для интерфейса сайта.
    ## Поддерживаемые языки:
    * **ru**: код русского языка.
    * **tm**: код туркменского языка.
    ## Возможная ошибка:
    * **400 Bad Request** - язык из куки отсутствует (не поддерживается).
    """
    if lang not in LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Language: {lang} is not supported. Use 'tm' or 'ru'.",
        )
    response.headers["Cache-Control"] = "private, max-age=3600"
    words = LANGUAGES[lang]
    return {
        key.removeprefix("ff_").lower(): value
        for key, value in words.__dict__.items()
        if key.startswith("ff_")
    }
