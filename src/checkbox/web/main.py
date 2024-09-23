from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from checkbox.config import Settings
from checkbox.di import MainProvider, ServiceProvider
from checkbox.di.auth import AuthProvider
from checkbox.web.exception_handlers import add_exception_handlers
from checkbox.web.routers import include_routers

settings = Settings()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

include_routers(app)
add_exception_handlers(app)

di_container = make_async_container(
    MainProvider(), ServiceProvider(), AuthProvider(), context={Settings: settings}
)
setup_dishka(container=di_container, app=app)
