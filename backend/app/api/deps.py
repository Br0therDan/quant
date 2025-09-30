from app.services.auth_service import fastapi_users

current_active_user = fastapi_users.current_user(active=True)


def get_current_active_verified_user():
    return fastapi_users.current_user(active=True, verified=True)


def get_current_active_superuser():
    return fastapi_users.current_user(active=True, superuser=True)
