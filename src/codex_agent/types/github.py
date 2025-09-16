import json
from pathlib import Path

from pydantic import Field, BaseModel, ConfigDict


class GitHubUser(BaseModel):
    login: str = Field(..., description="GitHub user login", examples=["octocat"])


class GitHubRepository(BaseModel):
    model_config = ConfigDict(extra="allow")

    full_name: str = Field(
        ..., description="Full name of the repository", examples=["octo-org/example"]
    )
    clone_url: str = Field(
        ..., description="HTTPS clone URL", examples=["https://github.com/octo-org/example.git"]
    )


class GitHubIssue(BaseModel):
    model_config = ConfigDict(extra="allow")

    number: int = Field(..., description="Issue number", examples=[42])
    title: str = Field(..., description="Issue title", examples=["Bug report"])
    html_url: str = Field(
        ...,
        description="Issue web URL",
        examples=["https://github.com/octo-org/example/issues/42"],
    )


class GitHubComment(BaseModel):
    model_config = ConfigDict(extra="allow")

    body: str = Field(..., description="Comment body")
    html_url: str | None = Field(
        default=None,
        description="Comment web URL",
        examples=["https://github.com/octo-org/example/issues/42#issuecomment-1"],
    )
    user: GitHubUser = Field(..., description="Author of the comment")


class GithubWebhookPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    action: str | None = Field(default=None, description="Action name", examples=["created"])
    comment: GitHubComment | None = Field(default=None, description="Issue comment object")
    issue: GitHubIssue | None = Field(default=None, description="Issue metadata")
    repository: GitHubRepository = Field(..., description="Repository associated with the event")
    sender: GitHubUser | None = Field(default=None, description="User that triggered the event")

    def save(self, filename: str) -> None:
        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.model_dump(exclude_unset=True, exclude_defaults=True), f, indent=4)
