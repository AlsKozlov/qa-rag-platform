import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app

@pytest.mark.asyncio
async def test_dialog_api_full():
    with patch("app.services.rag_service.RAGService.get_answer", new_callable=AsyncMock) as mock_get_answer, \
         patch("app.services.rag_service.publish_broker_msg", new_callable=AsyncMock) as mock_publish_broker, \
         patch("app.services.rag_service.vectorize_question", return_value="vector"), \
         patch("app.services.rag_service.vector_to_text", return_value="context"), \
         patch("app.services.rag_service.DialogRepository.find_one_or_none_by_conversation_id", new_callable=AsyncMock) as mock_find_dialog:

        mock_get_answer.return_value = "Mocked Answer"
        mock_find_dialog.return_value = MagicMock(dialog_history="previous history")

        async with AsyncClient(app=app, base_url="http://test") as ac:
            payload = {
                "question": "Explain RAG",
                "conversation_id": 1,
                "system_prompt": "You are helpful"
            }
            response = await ac.post("/api/rag/dialog", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert isinstance(data["answer"], str)
            assert data["answer"] == "Mocked Answer"

            mock_get_answer.assert_awaited_once()
            mock_publish_broker.assert_not_called()  
            mock_find_dialog.assert_awaited_once()
