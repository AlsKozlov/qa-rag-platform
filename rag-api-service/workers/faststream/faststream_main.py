from faststream import FastStream
from faststream.redis import RedisBroker
from app.config import settings
from app.services.llm.yandex_client import YandexLLMClient
from app.services.llm.local_client import LocalLLMClient
from app.services.llm.giga_client import GigaChatLLMClient
from app.services.rag_service import RAGService
from app.services.repositories.dialog_repository import DialogRepository
from app.services.base_service import get_current_date_time
from database.database import get_session


broker = RedisBroker(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
faststream_app = FastStream(broker)


llm_client_registry = {
    "YandexLLMClient": YandexLLMClient,
    "LocalLLMClient": LocalLLMClient,
    "GigaChatLLMClient": GigaChatLLMClient
}


async def run_faststream():
    await faststream_app.run()


def create_llm_client(class_name: str):
    llm_class = llm_client_registry.get(class_name)
    if not llm_class:
        raise ValueError(f"Unsupported LLM class: {class_name}")
    return llm_class()


@broker.subscriber(settings.ADD_HISTORY_TOPIC_NAME)
async def add_history(message: dict):
    conversation_id = message["conversation_id"]
    question = message["question"]
    answer = message["answer"]
    llm_class_name = message.get("llm_class", "LocalLLMClient")

    user_msg = f"Вопрос: {question}. Ответ: {answer}"

    llm_client = create_llm_client(llm_class_name)
    rag_service = RAGService(llm_client)

    summarized_text = await rag_service.llm_client.get_answer(
        settings.SUMM_SYSTEM,
        user_msg
    )

    session = get_session()
    await DialogRepository.add(
        conversation_id=conversation_id,
        date_time_answer=get_current_date_time(),
        dialog_history=summarized_text,
        session=session
    )
    await session.commit()


@broker.subscriber(settings.UPDATE_HISTORY_TOPIC_NAME)
async def update_dialog(message: dict):
    conversation_id = message["conversation_id"]
    dialog = message["dialog"]
    question = message["question"]
    answer = message["answer"]
    llm_class_name = message.get("llm_class", "LocalLLMClient")

    user_msg = f"Диалог: {dialog} Вопрос: {question}. Ответ: {answer}"

    llm_client = create_llm_client(llm_class_name)
    rag_service = RAGService(llm_client)

    summarized_text = await rag_service.llm_client.get_answer(
        settings.SUMM_SYSTEM,
        user_msg
    )

    session = get_session()
    await DialogRepository.update_by_conversation_id(
        conversation_id=conversation_id,
        date_time_answer=get_current_date_time(),
        history=summarized_text,
        session=session
        )
    await session.commit()
