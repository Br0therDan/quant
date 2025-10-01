from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from fastapi_users import exceptions, models, schemas
from fastapi_users.authentication import Authenticator
from fastapi_users.manager import BaseUserManager
from fastapi_users.router.common import ErrorCode, ErrorModel

from app.api.deps import get_current_active_superuser, get_current_active_verified_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.services.auth_service import (
    auth_backend as backend,
    fastapi_users,
)

authenticator = Authenticator(
    backends=[backend], get_user_manager=fastapi_users.get_user_manager
)
user_manager = fastapi_users.get_user_manager
get_current_user_token = authenticator.current_user_token(active=True, verified=True)

router = APIRouter()


async def get_user_or_404(
    id: str,
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(
        fastapi_users.get_user_manager
    ),
) -> models.UP:
    try:
        parsed_id = user_manager.parse_id(id)
        return await user_manager.get(parsed_id)
    except (exceptions.UserNotExists, exceptions.InvalidID) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@router.get(
    "/me",
    response_model=UserRead,
    name="users:current_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
    },
)
async def me(
    user: User = Depends(get_current_active_verified_user),
):
    return schemas.model_validate(UserRead, user)


@router.patch(
    "/me",
    response_model=UserRead,
    dependencies=[Depends(get_current_active_verified_user)],
    name="users:patch_current_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_me(
    request: Request,
    user_update: UserUpdate,  # type: ignore
    user: models.UP = Depends(get_current_active_verified_user),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(
        fastapi_users.get_user_manager
    ),
):
    try:
        user = await user_manager.update(user_update, user, safe=True, request=request)
        return schemas.model_validate(UserRead, user)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )


@router.get(
    "/{id}",
    response_model=UserRead,
    dependencies=[Depends(get_current_active_superuser)],
    name="users:user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
async def get_user(user=Depends(get_user_or_404)):
    return schemas.model_validate(UserRead, user)


@router.patch(
    "/{id}",
    response_model=UserRead,
    dependencies=[Depends(get_current_active_superuser)],
    name="users:patch_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                    "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_user(
    user_update: UserUpdate,  # type: ignore
    request: Request,
    user=Depends(get_user_or_404),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(
        fastapi_users.get_user_manager
    ),
):
    try:
        user = await user_manager.update(user_update, user, safe=False, request=request)
        return schemas.model_validate(UserRead, user)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(get_current_active_superuser)],
    name="users:delete_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a superuser.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
async def delete_user(
    request: Request,
    user=Depends(get_user_or_404),
    user_manager: BaseUserManager[models.UP, models.ID] = Depends(
        fastapi_users.get_user_manager
    ),
):
    await user_manager.delete(user, request=request)
    return None
