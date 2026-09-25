from pydantic import BaseModel, Field
from typing import List, Optional

class EventCreateSchema(BaseModel):
    page: str
    description: Optional[str] = Field(default="my description")


class EventUpdateSchema(BaseModel):
    description: str
    page: Optional[str] = ""


class EventSchema(BaseModel):
    id: int
    page: Optional[str] = ""
    description: Optional[str] = ""


class EventListSchema(BaseModel):
    results: List[EventSchema]
    count: int