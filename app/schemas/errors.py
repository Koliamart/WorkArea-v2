from pydantic import BaseModel


class ErrorDetails(BaseModel):
    field: str | None = None
    reason: str | None = None


class BaseError(BaseModel):
    code: int
    message: str
    details: ErrorDetails | dict | None = None
