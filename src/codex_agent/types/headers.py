from pydantic import Field, BaseModel, AliasChoices


class WebhookHeaders(BaseModel):
    host: str = Field(
        default="",
        description="Request host (authority) header.",
        examples=["mtktma:8116"],
        validation_alias=AliasChoices("host"),
        serialization_alias="host",
        exclude=True,
    )
    user_agent: str = Field(
        default="",
        description="Client user agent identifier.",
        examples=["Go-http-client/1.1"],
        validation_alias=AliasChoices("user-agent"),
        serialization_alias="user-agent",
    )
    content_length: str = Field(
        default="",
        description="Length of request body in bytes.",
        examples=["76", "81"],
        validation_alias=AliasChoices("content-length"),
        serialization_alias="content-length",
        exclude=True,
    )
    content_type: str = Field(
        default="",
        description="Request payload media type.",
        examples=["application/json"],
        validation_alias=AliasChoices("content-type"),
        serialization_alias="content-type",
    )


class GiteaWebhookHeaders(WebhookHeaders): ...


class GitHubWebhookHeaders(WebhookHeaders):
    github_event: str = Field(
        ...,
        description="Type of GitHub event",
        examples=["issue_comment"],
        validation_alias=AliasChoices("x-github-event", "X-GitHub-Event"),
        serialization_alias="X-GitHub-Event",
    )
    github_delivery: str | None = Field(
        default=None,
        description="Unique delivery identifier",
        examples=["1a2b3c4d"],
        validation_alias=AliasChoices("x-github-delivery", "X-GitHub-Delivery"),
        serialization_alias="X-GitHub-Delivery",
        exclude=True,
    )
    hub_signature_256: str | None = Field(
        default=None,
        description="HMAC signature for the payload",
        examples=["sha256=..."],
        validation_alias=AliasChoices("x-hub-signature-256", "X-Hub-Signature-256"),
        serialization_alias="X-Hub-Signature-256",
    )


__all__ = ["GitHubWebhookHeaders", "GiteaWebhookHeaders"]
