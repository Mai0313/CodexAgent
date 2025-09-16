import datetime

import jwt
from pydantic import BaseModel


class JWTHandler(BaseModel):
    app_id: str
    key: str

    async def generate_jwt(self) -> str:
        """產生 GitHub App JWT"""
        now = datetime.datetime.now(datetime.timezone.utc)
        exp = now + datetime.timedelta(minutes=10)
        token = jwt.encode(
            payload={"iat": now, "exp": exp, "iss": self.app_id}, key=self.key, algorithm="RS256"
        )
        return token
