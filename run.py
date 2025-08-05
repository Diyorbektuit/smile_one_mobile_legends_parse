from fastapi import FastAPI

from apis.routers import router

app = FastAPI()

app.include_router(router)