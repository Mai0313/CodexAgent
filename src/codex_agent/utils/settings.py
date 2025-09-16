from pathlib import Path
from functools import cached_property

import dotenv
from pydantic import Field, AliasChoices, computed_field
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class GithubAppSettings(BaseSettings):
    app_slug: str = Field(..., validation_alias=AliasChoices("GITHUB_APP_SLUG"))
    webhook_secret: str = Field(..., validation_alias=AliasChoices("GITHUB_APP_WEBHOOK_SECRET"))
    app_id: str = Field(..., validation_alias=AliasChoices("GITHUB_APP_ID"))
    client_id: str = Field(..., validation_alias=AliasChoices("GITHUB_CLIENT_ID"))
    client_secret: str = Field(..., validation_alias=AliasChoices("GITHUB_CLIENT_SECRET"))
    private_key_path: str = Field(
        default="./configs/app.pem", validation_alias=AliasChoices("GITHUB_PRIVATE_KEY_PATH")
    )

    @computed_field
    @cached_property
    def private_key(self) -> str:
        private_key = Path(self.private_key_path).read_text()
        return private_key


class Settings(GithubAppSettings): ...


__all__ = ["Settings"]
