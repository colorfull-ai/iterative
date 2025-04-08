from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base user model with common fields."""
    name: str
    description: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None

class UserCreate(UserBase):
    """user creation model."""
    pass

class User(UserBase):
    """user model with ID."""
    id: int

    class Config:
        orm_mode = True
