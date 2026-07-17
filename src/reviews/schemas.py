from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime


class ReviewModel(BaseModel):
    uid: uuid.UUID
    rating: int
    review_text: str
    user_uid: Optional[uuid.UUID] = None
    book_uid: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime  # fixed: was 'update_at' (typo)

    model_config = {"from_attributes": True}


class ReviewCreateModel(BaseModel):
    rating: int = Field(ge=1, le=5)  # fixed: was lt=5 (excluded 5, allowed 0)
    review_text: str
