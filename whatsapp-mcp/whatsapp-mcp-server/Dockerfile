FROM python:3.11 
# Python 3.11 might have vulnerabilities, considering trying a different ver.
WORKDIR /app

# Install base tools
RUN apt-get update && \
    apt-get install -y ffmpeg curl git

# Install uv and expose it globally
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    cp /root/.local/bin/uv /usr/local/bin/uv

# Copy backend code
COPY . .

# ✅ Copy frontend dist folder
COPY whatsapp-dashboard/dist /app/whatsapp-mcp-server/ui

WORKDIR /app/whatsapp-mcp-server

# Install Python deps
RUN uv pip install --system -r pyproject.toml

# Run the app
CMD ["uv", "run", "main.py"]
