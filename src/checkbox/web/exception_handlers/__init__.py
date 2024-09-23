from fastapi import FastAPI

from . import checkbox_exception


def add_exception_handlers(app: FastAPI) -> None:
    checkbox_exception.add_handler(app)
