import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.rag_service import RAGService

@pytest.mark.asyncio
async def test_get_answer_with_existing_dialog():
    llm_client = AsyncMock()
    llm_client.get_answer.return_value = "Mocked LLM Answer"

    session = MagicMock()
    with patch("app.services.rag_service.DialogRepository.find_one_or_none_by_conversation_id", new_callable=AsyncMock) as mock_find_dialog, \
         patch("app.services.rag_service.publish_broker_msg", new_callable=AsyncMock) as mock_publish, \
         patch("app.services.rag_service.vectorize_question", return_value="vector"), \
         patch("app.services.rag_service.vector_to_text", return_value="context"):

        mock_find_dialog.return_value = MagicMock(dialog_history="previous history")
        service = RAGService(llm_client)

        answer = await service.get_answer(
            question="What is RAG?",
            conversation_id=1,
            system_prompt="You are helpful",
            session=session
        )

        llm_client.get_answer.assert_awaited_once()
        mock_publish.assert_awaited_once()
        assert answer == "Mocked LLM Answer"


@pytest.mark.asyncio
async def test_get_answer_without_existing_dialog():
    llm_client = AsyncMock()
    llm_client.get_answer.return_value = "Mocked Answer No History"

    session = MagicMock()
    with patch("app.services.rag_service.DialogRepository.find_one_or_none_by_conversation_id", new_callable=AsyncMock) as mock_find_dialog, \
         patch("app.services.rag_service.publish_broker_msg", new_callable=AsyncMock) as mock_publish, \
         patch("app.services.rag_service.vectorize_question", return_value="vector"), \
         patch("app.services.rag_service.vector_to_text", return_value="context"):
        
        mock_find_dialog.return_value = None
        service = RAGService(llm_client)

        answer = await service.get_answer(
            question="What is RAG?",
            conversation_id=2,
            system_prompt="System prompt",
            session=session
        )

        llm_client.get_answer.assert_awaited_once()
        mock_publish.assert_awaited_once()
        assert answer == "Mocked Answer No History"
