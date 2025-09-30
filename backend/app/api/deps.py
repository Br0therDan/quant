from fastapi import Depends
from app.models.user import User
from app.services.auth_service import fastapi_users

current_active_user = fastapi_users.current_user(active=True)


def get_current_active_verified_user(current_user: User = Depends(current_active_user)):
    if not current_user.is_verified:
        raise Exception("User is not verified")
    return current_user


def get_current_active_superuser(current_user: User = Depends(current_active_user)):
    if not current_user.is_superuser:
        raise Exception("User is not a superuser")
    return current_user
