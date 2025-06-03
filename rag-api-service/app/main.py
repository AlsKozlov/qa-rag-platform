from fastapi import FastAPI
from routers.rest.api_rag.dialog_router import router as dialog_router
from routers.rest.api_rag.giga_rag_api import router as giga_router
from routers.rest.api_rag.yandex_rag_api import router as yandex_router
from routers.rest.api_rag.local_rag_api import router as local_router
import asyncio
from workers.faststream.faststream_main import run_faststream

app = FastAPI()
app.include_router(dialog_router)
app.include_router(giga_router)
app.include_router(yandex_router)
app.include_router(local_router)

@app.on_event("startup")
async def start_background_tasks():
    loop = asyncio.get_running_loop()
    loop.create_task(run_faststream)