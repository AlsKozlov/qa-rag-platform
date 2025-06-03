from fastapi import FastAPI
from routers.rest.bi_encoder_router import router as encoder_router

app = FastAPI()
app.include_router(encoder_router)

