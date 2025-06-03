from fastapi import FastAPI
from routers.rest.routers.vllm_router import router as transcribe_router


app = FastAPI()
app.include_router(transcribe_router)