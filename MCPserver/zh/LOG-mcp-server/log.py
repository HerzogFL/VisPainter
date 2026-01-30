from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import os
from typing import Optional
from mcp.server.fastmcp import Context, FastMCP


@asynccontextmanager
async def lifespan(app) -> AsyncIterator[None]:
    print("Starting Agent Output Logger service...")
    try:
        yield
    finally:
        print("Shutting down Agent Output Logger service...")


mcp = FastMCP("AgentOutputLogger", dependencies=[], lifespan=lifespan)


@mcp.tool()
def log_agent_output(ctx: Context, output: str, log_file_path: Optional[str] = None) -> str:
    """
    记录 agent 的输出内容到 txt 文件中。

    参数:
    - output: agent 的输出内容。
    - log_file_path: 可选，日志文件的路径。如果未提供，默认使用 'agent_output.log'。

    返回:
    - 一条消息，指示日志记录成功或失败。
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
    