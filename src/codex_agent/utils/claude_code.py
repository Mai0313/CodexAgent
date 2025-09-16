import os
from typing import TYPE_CHECKING
from pathlib import Path
import datetime
import platform
from functools import cached_property
from collections.abc import AsyncGenerator

from pydantic import Field, BaseModel, computed_field, model_validator
from claude_code_sdk import ClaudeCodeOptions, query

if TYPE_CHECKING:
    from claude_code_sdk.types import McpServerConfig


class ClaudeCodeHandler(BaseModel):
    task: str
    clone_url: str
    workspace: Path = Field(default=Path("./workspace"), exclude=True)

    @computed_field
    @cached_property
    def system_prompt(self) -> str:
        system_prompt = Path("./prompts/system_prompt.md").read_text()
        system_info = Path("./prompts/system_info.md").read_text()
        system_info = system_info.format(
            os_version=platform.platform(),
            current_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            shell=os.environ.get("SHELL") or os.environ.get("COMSPEC"),
            workspace_path=os.getcwd(),
        )
        return f"{system_prompt}\n{system_info}"

    @model_validator(mode="after")
    def _setup_task(self) -> "ClaudeCodeHandler":
        prompt = Path("./prompts/template.md").read_text()
        self.task = prompt.format(task=self.task, clone_url=self.clone_url)
        return self

    @model_validator(mode="after")
    def _setup_workspace(self) -> "ClaudeCodeHandler":
        repo_name = self.clone_url.split("/")[-1].replace(".git", "")
        self.workspace = Path(f"./workspaces/{repo_name}")
        if not self.workspace.exists():
            os.system(f"git clone {self.clone_url} {self.workspace}")  # noqa: S605
        return self

    async def run(self, prompt: str) -> AsyncGenerator[str, None]:
        mcp_servers: dict[str, McpServerConfig] = {
            "context7": {
                "type": "http",
                "url": "https://mcp.context7.com/mcp",
                "headers": {"CONTEXT7_API_KEY": "YOUR_API_KEY"},
            }
        }
        options = ClaudeCodeOptions(
            allowed_tools=["*"],
            system_prompt=self.system_prompt,
            mcp_servers=mcp_servers,
            permission_mode="bypassPermissions",
            max_turns=1,
            cwd=self.workspace.absolute().as_posix(),
        )

        async for message in query(prompt=prompt, options=options):
            yield message
