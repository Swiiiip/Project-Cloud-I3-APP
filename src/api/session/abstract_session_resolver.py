from abc import ABC, abstractmethod
from typing import Optional

from fastapi import Request, Response


class AbstractSessionResolver(ABC):
    @abstractmethod
    async def resolve(self, request: Request, response: Response, session_id: Optional[str]) -> str:
        pass

