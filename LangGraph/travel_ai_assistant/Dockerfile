# Travel AI Assistant — Dockerfile
# Requires: Ollama running on the host machine

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Remove virtual env if accidentally copied (we use system pip above)
RUN rm -rf .venv

# Don't run as root
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8008

# Start the web server on port 8008
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8008"]
