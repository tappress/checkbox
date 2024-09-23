from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from checkbox.exceptions.base import CheckboxException


def add_handler(app: FastAPI):
    @app.exception_handler(CheckboxException)
    async def handler(request: Request, exc: CheckboxException):
        return JSONResponse(
            status_code=exc.HTTP_STATUS,
            content={"detail": exc.message, "code": exc.CODE},
        )
