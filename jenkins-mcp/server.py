from fastmcp import FastMCP

from tools.jobs import list_jobs
from tools.builds import trigger_build, last_build, console_logs
from tools.pipeline import failed_jobs
from tools.analysis import analyze_failed_build, summarize_build_status

mcp = FastMCP("Jenkins MCP")


@mcp.tool()
def get_jobs():
    """Return all Jenkins jobs"""
    return list_jobs()


@mcp.tool()
def build(job_name: str):
    """Trigger a Jenkins build"""
    return trigger_build(job_name)


@mcp.tool()
def get_last_build(job_name: str):
    """Get last build information"""
    return last_build(job_name)


@mcp.tool()
def get_logs(job_name: str):
    """Get build console logs"""
    return console_logs(job_name)


@mcp.tool()
def get_failed_jobs():
    """Return all failed jobs"""
    return failed_jobs()


@mcp.tool()
def analyze_build(job_name: str):
    """Analyze failed build logs using Ollama AI"""
    return analyze_failed_build(job_name)


@mcp.tool()
def summarize_build(job_name: str):
    """Get AI-powered build summary using Ollama"""
    return summarize_build_status(job_name)


if __name__ == "__main__":
    mcp.run()
