from fastapi import FastAPI

from . import receipts
from . import users


def include_routers(app: FastAPI) -> None:
    app.include_router(users.router)
    app.include_router(receipts.router)
