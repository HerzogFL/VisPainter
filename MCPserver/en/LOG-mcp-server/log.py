from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import os
from typing import Optional
from mcp.server.fastmcp import Context, FastMCP


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    # Operations at startup
    print("Starting Agent Output Logger service...")
    try:
        yield  # During service operation
    finally:
        # Operations at shutdown
        print("Shutting down Agent Output Logger service...")


mcp = FastMCP("AgentOutputLogger", dependencies=[], lifespan=lifespan)


@mcp.tool()
def log_agent_output(ctx: Context, output: str, log_file_path: Optional[str] = None) -> str:
    """
    Log the agent's output content to a txt file.

    Parameters:
    - output: The content produced by the agent.
    - log_file_path: Optional, the path to the log file. If not provided, defaults to 'agent_output.log'.

    Returns:
    - A message indicating whether the logging was successful or failed.
    """
    if log_file_path is None:
        log_file_path = 'agent_output.log'

    try:
        with open(log_file_path, 'a') as log_file:
            log_file.write(output + '\n')
        return f"Agent output successfully logged to {log_file_path}"
    except Exception as e:
        return f"Logging agent output failed: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')