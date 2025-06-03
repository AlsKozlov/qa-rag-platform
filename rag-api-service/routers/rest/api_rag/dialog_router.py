from fastapi import APIRouter, Depends
from app.services.dialog_service import DialogService
from database.database import get_session

router = APIRouter(prefix="/dialog", tags=["Dialog"])

@router.delete("/clear_history")
async def clear_history(conversation_id: int, 
                        session = Depends(get_session)):
    await DialogService.clear_history(conversation_id, session)
    return {"status": "history cleared"}
