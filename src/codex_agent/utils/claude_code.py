from typing import TYPE_CHECKING
from pathlib import Path
from functools import cached_property
from collections.abc import AsyncGenerator

from pydantic import BaseModel, computed_field
from claude_code_sdk import ClaudeCodeOptions, query

if TYPE_CHECKING:
    from claude_code_sdk.types import McpServerConfig


class ClaudeCodeHandler(BaseModel):
    @computed_field
    @cached_property
    def system_prompt(self) -> str:
        prompt_path = Path("./prompts/default.md")
        return prompt_path.read_text()

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
        )

        async for message in query(prompt=prompt, options=options):
            yield message
