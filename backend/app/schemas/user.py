import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    fullname: str | None = None


class UserCreate(schemas.BaseUserCreate):
    fullname: str | None = None


class UserUpdate(schemas.BaseUserUpdate):
    fullname: str | None = None
