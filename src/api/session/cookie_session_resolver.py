import uuid
from typing import Optional

from fastapi import HTTPException, Request, Response

from src.api.session.abstract_session_resolver import AbstractSessionResolver


class CookieSessionResolver(AbstractSessionResolver):
    async def resolve(self, request: Request, response: Response, session_id: Optional[str]) -> str:
        if session_id:
            return session_id

        if "/start" in request.url.path:
            new_id = str(uuid.uuid4())
            response.set_cookie(key="session_id", value=new_id, path="/")
            return new_id

        raise HTTPException(status_code=403, detail="No active session found. Visit /start first.")

