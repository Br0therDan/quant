from beanie import Document

# from fastapi_users_db_beanie import BeanieBaseUserDocument
from fastapi_users.db import BeanieBaseUser
from typing import Optional

from fastapi_users_db_beanie import BaseOAuthAccount
from pydantic import Field


class OAuthAccount(BaseOAuthAccount):
    pass


class User(BeanieBaseUser, Document):
    """User model for authentication and authorization"""

    # BeanieBaseUserDocument에서 이미 email 필드가 정의되어 있으므로
    # 추가로 정의할 필요 없음. 다만 명시적으로 타입을 지정할 수 있음
    fullname: Optional[str] = None

    oauth_accounts: list[OAuthAccount] = Field(default_factory=list)

    class Settings:
        name = "users"  # MongoDB 컬렉션 이름
        # BeanieBaseUserDocument의 기본 인덱스 상속
