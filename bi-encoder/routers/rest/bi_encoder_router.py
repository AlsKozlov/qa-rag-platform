from fastapi import APIRouter
from app.model import BI_ENCODER
from app.service import encode_process
from routers.rest.scheme import EncoderRequest, EncoderResponse


router = APIRouter(
   tags=["Encode incoming text"]
)

@router.post("/api/encode")
async def get_answer(req: EncoderRequest) -> EncoderResponse:
   vector = encode_process(BI_ENCODER, req.chunk)
   vector = vector.numpy().tolist()

   return EncoderResponse(vector=vector)
