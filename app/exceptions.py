from fastapi import status


class AppBaseException(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail


class AccessDenied(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class CodeTimeOut(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail=detail)


class InvalidCode(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidPassword(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidEmail(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail
        )


class InvalidUsername(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail
        )


class EntityNotFound(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ExercisesNotFound(AppBaseException):
    def __init__(self, detail: str, missing_ids: list[int]) -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        self.missing_ids = missing_ids


class EmptyRequestedObject(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class LimitReached(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UniqueError(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class Unauthorized(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UnprocessableContent(AppBaseException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail
        )
