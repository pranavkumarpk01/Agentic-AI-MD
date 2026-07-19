# Jenkins MCP Server

A Model Context Protocol (MCP) server for Jenkins CI/CD integration with Ollama AI support for intelligent build analysis.

## Features

- List all Jenkins jobs
- Trigger builds
- Get last build information
- Fetch console logs
- Identify failed jobs
- **AI-powered analysis** using Ollama (analyze logs, summarize builds)

## Prerequisites

- Python 3.8+
- Jenkins instance running
- Ollama installed and running locally
- pip for package management

## Installation

### 1. Clone/Setup Project
```bash
cd /path/to/jenkins-mcp
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Ollama

**macOS:**
```bash
# Download from https://ollama.ai
# Or via Homebrew:
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download installer from https://ollama.ai

### 5. Start Ollama

```bash
ollama serve
```

In another terminal, pull a model (mistral is default):
```bash
ollama pull mistral
```

Other available models: `llama2`, `neural-chat`, `dolphin-mixtral`

### 6. Configure Environment

Edit `.env` file with your Jenkins credentials:

```env
JENKINS_URL=http://localhost:8080
JENKINS_USER=admin
JENKINS_TOKEN=YOUR_JENKINS_API_TOKEN

OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

**Getting Jenkins API Token:**
1. Go to http://localhost:8080
2. Click your username → Configure
3. Click "Add new Token" under API Token
4. Copy the token to `.env`

## Running

### Start the MCP Server
```bash
python server.py
```

The server will start and await connections from Claude or other MCP clients.

### Docker Setup (Optional)

Start Jenkins with Docker:
```bash
docker-compose up -d
```

This starts Jenkins on `http://localhost:8080`

## Available Tools

### get_jobs()
Returns all Jenkins jobs with their names and URLs.

### build(job_name)
Triggers a new build for the specified job.

### get_last_build(job_name)
Retrieves information about the last build (status, duration, timestamp).

### get_logs(job_name)
Fetches the complete console output of the last build.

### get_failed_jobs()
Lists all jobs with their most recent failed build.

### analyze_build(job_name)
**AI-Powered**: Analyzes the last build's logs using Ollama and identifies issues, errors, and problems.

### summarize_build(job_name)
**AI-Powered**: Generates an AI summary of the last build's status and results.

## Architecture

```
jenkins-mcp/
├── server.py              # FastMCP server entry point
├── config.py              # Configuration from environment
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── docker-compose.yml     # Docker setup for Jenkins
├── tools/
│   ├── __init__.py
│   ├── jobs.py           # Job listing functions
│   ├── builds.py         # Build management
│   ├── pipeline.py       # Pipeline analysis
│   └── analysis.py       # Ollama-based analysis
└── utils/
    ├── __init__.py
    ├── jenkins_client.py # Jenkins API wrapper
    └── llm_client.py     # Ollama API wrapper
```

## Usage with Claude

Once the MCP server is running, Claude can:

```
"Get all failed Jenkins jobs and analyze why they failed"
"Trigger the build for job X and summarize the results"
"What was the issue in the last build of job Y?"
```

## Troubleshooting

### Ollama not responding
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if stopped
ollama serve
```

### Jenkins connection failed
- Verify Jenkins URL is correct
- Check Jenkins is running: `curl http://localhost:8080`
- Verify API token is valid

### Model not found
```bash
# List available models
ollama list

# Pull a model
ollama pull mistral
```

### Python import errors
```bash
# Reinstall requirements
pip install --upgrade -r requirements.txt
```

## Development

To add new tools:

1. Create a function in appropriate `tools/` file
2. Import and decorate with `@mcp.tool()` in `server.py`
3. Restart the server

## License

MIT
