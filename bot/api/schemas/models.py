from pydantic import BaseModel
from typing import Optional


class ItemResponse(BaseModel):
    id: int
    article: Optional[str] = None
    cross_number: Optional[str] = None
    name: str
    count: Optional[str] = None

    class Config:
        from_attributes = True
