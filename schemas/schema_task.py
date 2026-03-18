from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    
class TaskUserInfo(BaseModel):
    id: int
    email: str
    username: str
    model_config = ConfigDict(from_attributes=True)

class TaskResponseWithUser(TaskBase):
    id: int
    completed: bool
    user_id: int
    created_at: datetime
    owner: TaskUserInfo
    model_config = ConfigDict(from_attributes=True)

class TaskCreate(TaskBase):
    completed: bool = Field(default=False)

class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=100)
    completed: bool = Field(default=None)

class TaskResponse(TaskBase):
    id: int
    completed: bool
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)