from fastapi import FastAPI
from app.api import character

app = FastAPI()


@app.get("/")
async def index():
    return {"ping": "pong"}


app.include_router(character.router, prefix="/character", tags=["Characters"])
