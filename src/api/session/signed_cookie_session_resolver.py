import hashlib
import hmac
import uuid
from typing import Optional

from fastapi import HTTPException, Request, Response


class SignedCookieSessionResolver:
    def __init__(self, secret_key: str):
        self._secret_key = secret_key.encode("utf-8")

    async def resolve(self, request: Request, response: Response, cookie_value: Optional[str]) -> str:
        if cookie_value:
            session_id = self._verify(cookie_value)
            if session_id is not None:
                return session_id
            raise HTTPException(status_code=403, detail="Invalid session cookie")

        if "/start" in request.url.path:
            session_id = str(uuid.uuid4())
            response.set_cookie(key="session_id", value=self._sign(session_id), path="/")
            return session_id

        raise HTTPException(status_code=403, detail="No active session found. Visit /start first.")

    def _sign(self, session_id: str) -> str:
        digest = hmac.new(self._secret_key, session_id.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{session_id}.{digest}"

    def _verify(self, signed_cookie: str) -> Optional[str]:
        parts = signed_cookie.rsplit(".", 1)
        if len(parts) != 2:
            return None
        session_id, signature = parts
        expected = hmac.new(self._secret_key, session_id.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        return session_id

