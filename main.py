from contextlib import asynccontextmanager

from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import init_db
import requests as rq


@asynccontextmanager
async def lifespan(app_: FastAPI):
    await init_db()
    print('Bot is ready')
    yield


app = FastAPI(title="ToDoList", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,          # разрешаем всем доступ к API
    allow_origins=["*"],     # url разрешенных сайтов
    allow_credentials=True,  # разрешаем отправлять куки
    allow_methods=["*"],     # разрешенные методы
    allow_headers=["*"],     # разрешенные заголовки
)


@app.get("/api/tasks/{tg_id}")
async def tasks(tg_id: int):
    user = await rq.add_user(tg_id)
    return await rq.get_tasks(user.id)


@app.get('/api/main/{tg_id}')
async def main(tg_id: int):
    user = await rq.add_user(tg_id)
    completed_tasks_count = await rq.get_completed_tasks_count(user.id)
    return {
        'completedTasks': completed_tasks_count
    }



