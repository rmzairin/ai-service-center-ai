from fastapi import FastAPI
from api import health_api, chat_api

app = FastAPI()

app.include_router(health_api.router, prefix="/health", tags=["Health"])
app.include_router(chat_api.router, prefix="/api/chat", tags=["Chat"])


@app.get("/")
def root():
    return {"message": "AI Service Center - AI Engine is running"}