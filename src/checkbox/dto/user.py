from pydantic import BaseModel, EmailStr


class SignUpUserDto(BaseModel):
    email: EmailStr
    password: str


class SignInUserDto(BaseModel):
    email: EmailStr
    password: str


class RefreshTokensDto(BaseModel):
    refresh_token: str


class TokensResponseDto(BaseModel):
    access_token: str
    refresh_token: str
