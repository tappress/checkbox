from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from checkbox.dto.user import (
    SignUpUserDto,
    TokensResponseDto,
    SignInUserDto,
    RefreshTokensDto,
)
from checkbox.services.user import UserService

router = APIRouter(prefix="/users", route_class=DishkaRoute, tags=["User"])


@router.post("/sign-up")
async def sign_up(
    data: SignUpUserDto, user_service: FromDishka[UserService]
) -> TokensResponseDto:
    return await user_service.sign_up(data)


@router.post("/sign-in")
async def sign_in(
    data: SignInUserDto, user_service: FromDishka[UserService]
) -> TokensResponseDto:
    return await user_service.sign_in(data)


@router.post("/refresh-tokens")
async def refresh_tokens(
    data: RefreshTokensDto, user_service: FromDishka[UserService]
) -> TokensResponseDto:
    return await user_service.refresh_auth_tokens(refresh_token=data.refresh_token)
