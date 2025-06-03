from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    async def get_answer(self, 
                         system_msg: str, 
                         user_msg: str) -> str:
        pass
