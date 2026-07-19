# ✅ Claude Desktop Setup Complete

## Configuration Created
Your Claude desktop config has been automatically created at:
```
~/.claude/claude_desktop_config.json
```

## What's Inside
```json
{
  "mcpServers": {
    "jenkins-mcp": {
      "command": "python3",
      "args": ["/Users/pranav/Documents/Agentic AI/jenkins-mcp/server.py"]
    }
  }
}
```

---

## Quick Start Guide

### Step 1: Prerequisites
Ensure these are running:

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```

**Terminal 2 - Pull Mistral model (if not already done):**
```bash
ollama pull mistral
```

**Terminal 3 - Verify Jenkins is running:**
```bash
curl http://localhost:8080
```

### Step 2: Start Your MCP Server
```bash
cd /Users/pranav/Documents/Agentic\ AI/jenkins-mcp
source .venv/bin/activate
python server.py
```

The server will start and wait for Claude to connect.

### Step 3: Open Claude Desktop
1. Launch Claude desktop app
2. You should see a notification that Jenkins MCP server connected
3. Or check the bottom status bar for "jenkins-mcp" connection status

### Step 4: Start Asking Questions
Open a conversation and ask:

```
Get all my Jenkins jobs
```

```
What are the failed builds?
```

```
Analyze the last build of my-job-name
```

```
Summarize the build status for my-job-name
```

---

## Available Tools in Claude

Once connected, you have access to:

### Jenkins Management
- **get_jobs()** - List all jobs with URLs
- **build(job_name)** - Trigger a new build
- **get_last_build(job_name)** - Get last build info
- **get_logs(job_name)** - Fetch console logs
- **get_failed_jobs()** - List all failed jobs

### AI Analysis (Ollama Powered)
- **analyze_build(job_name)** - AI analyzes build logs, identifies issues
- **summarize_build(job_name)** - AI generates build summary

---

## Troubleshooting

### MCP Not Connecting?

**Check config file exists:**
```bash
cat ~/.claude/claude_desktop_config.json
```

**Restart Claude:**
- Quit Claude completely (Cmd+Q)
- Reopen Claude
- Server should auto-connect

**Check server is running:**
```bash
ps aux | grep "server.py"
```

### Jenkins Connection Failed?

**Verify Jenkins is running:**
```bash
curl http://localhost:8080
```

**Update .env with correct credentials:**
```bash
cd /Users/pranav/Documents/Agentic\ AI/jenkins-mcp
cat .env
# Update JENKINS_TOKEN if needed
```

### Ollama Not Responding?

**Start Ollama:**
```bash
ollama serve
```

**Pull model:**
```bash
ollama pull mistral
```

**Test connection:**
```bash
curl http://localhost:11434/api/tags
```

---

## Example Conversations in Claude

**Example 1: Get Failed Jobs**
```
User: Show me all failed Jenkins jobs
Claude: [Uses get_failed_jobs tool]
Output: List of jobs with FAILURE status
```

**Example 2: Analyze a Build**
```
User: What went wrong in the last build of my-deploy-job?
Claude: [Uses analyze_build tool + Ollama]
Output: AI analysis of build logs with specific issues
```

**Example 3: Build Summary**
```
User: Give me a summary of my-test-job's last build
Claude: [Uses summarize_build tool + Ollama]
Output: AI-powered summary with status and duration
```

---

## Architecture Diagram

```
Claude Desktop
    ↓
~/.claude/claude_desktop_config.json
    ↓
python server.py (FastMCP)
    ├─→ tools/ (Jenkins operations)
    ├─→ utils/jenkins_client.py (Jenkins API)
    └─→ utils/llm_client.py (Ollama AI)
```

---

## File Locations
- **MCP Server:** `/Users/pranav/Documents/Agentic AI/jenkins-mcp/server.py`
- **Config:** `~/.claude/claude_desktop_config.json`
- **Jenkins Client:** `/Users/pranav/Documents/Agentic AI/jenkins-mcp/utils/jenkins_client.py`
- **Ollama Client:** `/Users/pranav/Documents/Agentic AI/jenkins-mcp/utils/llm_client.py`
- **Environment:** `/Users/pranav/Documents/Agentic AI/jenkins-mcp/.env`

---

## Next Steps

1. ✅ Config file created
2. ⏳ Start Ollama: `ollama serve`
3. ⏳ Start MCP Server: `python server.py`
4. ⏳ Open Claude Desktop
5. ⏳ Ask your first question!

**You're all set! 🚀**
