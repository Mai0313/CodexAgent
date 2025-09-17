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


class GiteaAppSettings(BaseSettings):
    """Settings for Gitea OAuth application."""

    # Base URL of your Gitea instance, e.g. https://gitea.example.com
    gitea_base_url: str = Field(
        default="https://gitea.mediatek.inc", validation_alias=AliasChoices("GITEA_BASE_URL")
    )
    # OAuth client id/secret generated from Gitea -> Settings -> Applications
    gitea_client_id: str | None = Field(
        default=None, validation_alias=AliasChoices("GITEA_CLIENT_ID")
    )
    gitea_client_secret: str | None = Field(
        default=None, validation_alias=AliasChoices("GITEA_CLIENT_SECRET")
    )
    # Optional: redirect URI you configured in Gitea app. If set, we'll include it in token exchange
    gitea_redirect_uri: str | None = Field(
        default=None, validation_alias=AliasChoices("GITEA_REDIRECT_URI")
    )


class Settings(GithubAppSettings, GiteaAppSettings): ...


__all__ = ["Settings"]
