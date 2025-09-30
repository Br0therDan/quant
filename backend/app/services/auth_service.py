from beanie import PydanticObjectId
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from app.models.user import User
from app.core.config import settings
from app.services.user_manager import get_user_manager

SECRET = settings.SECRET_KEY


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


# def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, PydanticObjectId](get_user_manager, [auth_backend])
