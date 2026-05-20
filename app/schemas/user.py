from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    user_name: str
    job_title: str
    user_info: str | None = None


class UserPublic(BaseModel):
    id: int
    user_name: str = Field(min_length=1, max_length=70)
    job_title: str = Field(min_length=1, max_length=50)
    user_info: str | None = Field(default=None, max_length=300)


class PatchMeProfile(BaseModel):
    user_name: str | None = Field(default=None, min_length=1, max_length=70)
    job_title: str | None = Field(default=None, min_length=1, max_length=50)
    user_info: str | None = Field(default=None, max_length=300)
