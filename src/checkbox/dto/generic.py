from pydantic import BaseModel


class OffsetResponse[T](BaseModel):
    total: int
    items: list[T]
