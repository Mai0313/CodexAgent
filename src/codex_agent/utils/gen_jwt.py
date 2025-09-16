import datetime

import jwt
from pydantic import BaseModel


class JWTHandler(BaseModel):
    @staticmethod
    async def generate_jwt(app_id: str, key: str) -> str:
        """產生 GitHub App JWT"""
        now = datetime.datetime.now(datetime.timezone.utc)
        exp = now + datetime.timedelta(minutes=10)
        token = jwt.encode(
            payload={"iat": now, "exp": exp, "iss": app_id}, key=key, algorithm="RS256"
        )
        return token
