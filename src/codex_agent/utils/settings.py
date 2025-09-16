import dotenv
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class GithubAppSettings(BaseSettings):
    app_slug: str = Field(..., validation_alias=AliasChoices("GITHUB_APP_SLUG"))
    webhook_secret: str = Field(..., validation_alias=AliasChoices("GITHUB_APP_WEBHOOK_SECRET"))


class Settings(GithubAppSettings): ...


__all__ = ["Settings"]
