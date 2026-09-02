from contextlib import asynccontextmanager

from fastapi import FastAPI
from routes import auth, analyze, save_text_data
from database import engine, Base

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Анализ текста на эмоции", lifespan=lifespan)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(analyze.router, prefix="/api", tags=["Analyze"])
app.include_router(save_text_data.router, prefix="/api", tags=["Entries"])

@app.get("/")
def read_root():
    return {"message": "Сервер работает!"}
