from workers.faststream.publisher import publish_broker_msg
from app.services.base_service import vectorize_question, vector_to_text
from app.services.repositories.dialog_repository import DialogRepository
from app.services.llm.base import BaseLLMClient
from app.config import settings


class RAGService:
    def __init__(self, 
                 llm_client: BaseLLMClient):
        self.llm_client = llm_client


    async def get_answer(self, 
                         question: str, 
                         conversation_id: int, 
                         system_prompt: str,
                         session):
        topic_name = ""
        vec_q = vectorize_question(question)
        vec_context = vector_to_text(question, vec_q, 5)

        user_msg = f"{settings.QUESTION_MESSAGE}: {question}"
        broker_message = {"conversation_id": conversation_id,
                          "question": question,
                          "llm_class": self.llm_client.__class__.__name__}
        
        if vec_context:
            user_msg += f" {settings.QUESTION_DATABASE_MESSAGE}: {vec_context}"

        dialog = await DialogRepository.find_one_or_none_by_conversation_id(conversation_id, session)
        if dialog:
            user_msg += f" {settings.SUMM_MESSAGE}: {dialog.dialog_history}"
            broker_message["dialog"] = dialog.dialog_history
            topic_name = settings.UPDATE_HISTORY_TOPIC_NAME
        else:
            topic_name = settings.ADD_HISTORY_TOPIC_NAME

        answer = await self.llm_client.get_answer(system_prompt, 
                                                  user_msg)
        broker_message["answer"] = answer
    
        await publish_broker_msg(broker_message,
                                 topic_name)
        
        return answer