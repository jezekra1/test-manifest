#!/usr/bin/env python
import asyncio
import warnings
from datetime import datetime
from typing import Any

from beeai_sdk.providers.agent import run_agent_provider
from beeai_sdk.schemas.metadata import Metadata
from beeai_sdk.schemas.prompt import PromptInput, PromptOutput
from crewai.crew import CrewOutput
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

from crewai_agent.crew import CrewaiAgent

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

class Log(BaseModel):
    text: str
    metadata: Any = Field(default=None)


class Output(PromptOutput):
    logs: list[Log | None] = Field(default_factory=list)
    images: list[str | None] = Field(default_factory=list)
    text: str = Field(default_factory=str)


async def register_agent() -> int:
    server = FastMCP("researcher-agent")

    @server.agent(
        "Research Crew",
        "Uncover cutting-edge developments in a given topic",
        input=PromptInput,
        output=Output,
        **Metadata(title="Research Crew", framework="CrewAI", ui="chat", licence="Apache 2.0").model_dump(),
    )
    async def run_agent(input: PromptInput, ctx: Context) -> Output:
        loop = asyncio.get_event_loop()

        def step_callback(update, *args, **kwargs):
            if hasattr(update, "output"):
                delta = Output(text=update.output)
                asyncio.run_coroutine_threadsafe(ctx.report_agent_run_progress(delta=delta), loop)

        try:
            crew = CrewaiAgent().crew(step_callback=step_callback)
            inputs = {"topic": input.prompt, "current_year": datetime.now().year}
            result: CrewOutput = await asyncio.to_thread(crew.kickoff, inputs=inputs)
            return Output(text=result.raw)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

    await run_agent_provider(server)
    return 0

def main():
    asyncio.run(register_agent())