import httpx
from fastapi import Request, APIRouter, HTTPException
from rich.console import Console
from starlette.responses import RedirectResponse

from codex_agent.types.gitea import GiteaWebhookPayload
from codex_agent.types.headers import GiteaWebhookHeaders
from codex_agent.utils.settings import Settings
from codex_agent.utils.claude_code import ClaudeCodeHandler

router = APIRouter()

console = Console()
settings = Settings()


@router.post("/webhook")
async def handle_gitea_webhook(request: Request) -> dict[str, str]:
    GiteaWebhookHeaders(**dict(request.headers))
    body_dict = await request.json()

    payload = GiteaWebhookPayload(**body_dict)
    if payload.action != "created" or not payload.comment or not payload.comment.body:
        return {"status": "ignored"}
    if f"@{settings.app_slug}" not in payload.comment.body.lower():
        return {"status": "ignored"}
    if payload.action == "created" and payload.comment and payload.comment.user:
        console.print(payload)
        claude = ClaudeCodeHandler(
            task=payload.comment.body, clone_url=payload.repository.clone_url
        )
        console.print(claude.task)
    return {"status": "received"}


@router.get("/auth")
async def gitea_auth_callback(code: str, state: str | None = None) -> dict:
    """OAuth callback for Gitea.

    This exchanges the temporary `code` for an access token using the Gitea instance's
    /login/oauth/access_token endpoint.

    Notes:
    - You must create a Gitea OAuth app (user settings -> Applications) with a Redirect URI
      pointing to your deployed API, e.g. https://your.domain/gitea/auth
    - Set env vars GITEA_CLIENT_ID and GITEA_CLIENT_SECRET accordingly.
    """
    if not settings.gitea_client_id or not settings.gitea_client_secret:
        raise HTTPException(
            status_code=500, detail="Gitea OAuth is not configured: missing client id/secret"
        )

    token_url = f"{settings.gitea_base_url.rstrip('/')}/login/oauth/access_token"
    console.print("✅ Gitea OAuth callback received!")
    console.print(f"code={code}, state={state}")

    form = {
        "client_id": settings.gitea_client_id,
        "client_secret": settings.gitea_client_secret,
        "code": code,
    }
    if state:
        form["state"] = state
    if settings.gitea_redirect_uri:
        form["redirect_uri"] = settings.gitea_redirect_uri

    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, headers={"Accept": "application/json"}, data=form)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    token_data = resp.json()
    console.print("🔑 Gitea User Access Token:", token_data)
    return {"message": "Gitea OAuth callback received", "token": token_data}


@router.get("/me")
async def gitea_me(access_token: str, token_type: str = "Bearer") -> dict:
    """Fetch the current user from Gitea using a bearer token returned by /gitea/auth.

    Query param:
    - access_token: string returned by the token exchange.
    """
    api_url = f"{settings.gitea_base_url.rstrip('/')}/api/v1/user"
    # Gitea supports OAuth2 bearer tokens and PAT-style `token` header; prefer Bearer for OAuth2
    auth_prefix = token_type if token_type else "Bearer"
    headers = {"Authorization": f"{auth_prefix} {access_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(api_url, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)
    return resp.json()


@router.get("/login")
async def gitea_login(state: str | None = None) -> RedirectResponse:
    """Initiate OAuth login by redirecting to the Gitea authorize endpoint."""
    if not settings.gitea_client_id:
        raise HTTPException(
            status_code=500, detail="Gitea OAuth is not configured: missing client id"
        )
    authorize_url = f"{settings.gitea_base_url.rstrip('/')}/login/oauth/authorize"
    params = {"client_id": settings.gitea_client_id, "response_type": "code"}
    if settings.gitea_redirect_uri:
        params["redirect_uri"] = settings.gitea_redirect_uri
    if state:
        params["state"] = state

    # Build query string
    from urllib.parse import urlencode

    url = f"{authorize_url}?{urlencode(params)}"
    return RedirectResponse(url=url, status_code=302)
