from typing import NewType

from dishka import Provider, provide, Scope, from_context
from starlette.requests import Request

from checkbox.database.models import User
from checkbox.exceptions.base import Unauthorized
from checkbox.services.user import UserService

AccessToken = NewType("AccessToken", str)


class AuthProvider(Provider):
    settings = from_context(provides=Request, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST, provides=AccessToken)
    async def get_access_token(self, request: Request):
        token = request.headers.get("Authorization")

        if not token:
            raise Unauthorized("Credentials were not provided")

        token_parts = token.split()

        if len(token_parts) != 2:
            raise Unauthorized("Invalid credentials")

        return token_parts[1]

    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self,
        user_service: UserService,
        access_token: AccessToken,
    ) -> User:
        user_id = user_service.get_user_id_from_access_token(access_token)
        user = await user_service.get_by_id(user_id)
        return user
