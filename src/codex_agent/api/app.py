from fastapi import FastAPI

from codex_agent.api.v1 import gitea, github

app = FastAPI()
app.include_router(gitea.router, prefix="/gitea", tags=["gitea"])
app.include_router(github.router, prefix="/github", tags=["github"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello, Codex Agent is running!"}
