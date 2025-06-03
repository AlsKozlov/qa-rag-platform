from app.services.repositories.dialog_repository import DialogRepository

class DialogService:
    @staticmethod
    async def clear_history(conversation_id: int, 
                            session):
        await DialogRepository.delete_by_conversation_id(conversation_id, 
                                                         session)
        await session.commit()
