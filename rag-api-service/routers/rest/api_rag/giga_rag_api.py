from fastapi import APIRouter, Depends
from routers.rest.api_rag.schemes import LLMAPIRequest, LLMAPIResponse
from app.services.llm.giga_client import GigaChatLLMClient
from database.database import get_session
from app.services.rag_service import RAGService
from app.config import settings

router = APIRouter(prefix="/giga", tags=["Local RAG"])

def get_rag_service() -> RAGService:
    return RAGService(GigaChatLLMClient())

@router.post("/get_answer")
async def get_answer(req: LLMAPIRequest, 
                     rag_service: RAGService = Depends(get_rag_service),
                     session = Depends(get_session)):
    answer = await rag_service.get_answer(
        question=req.question,
        conversation_id=req.conversation_id,
        collection_name=settings.COLLECTION_NAME,
        system_prompt=settings.RAG_SYSTEM,
        session=session
    )
    return LLMAPIResponse(answer=answer)
