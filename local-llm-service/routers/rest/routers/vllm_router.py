from fastapi import APIRouter
from app.service import run_inference
from routers.rest.routers.dto.schemes import LocalModelRequest

router = APIRouter(
    prefix="/api",
    tags=["local model service"]
)

@router.post("/get_answer")
async def get_answer(req: LocalModelRequest):
    return run_inference(req.system_msg,
                         req.user_msg,
                         req.temperature,
                         req.top_p,
                         req.max_tokens)