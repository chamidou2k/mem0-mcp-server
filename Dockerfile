FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mem0_mcp_server.py .
COPY start.sh .
RUN chmod +x start.sh

EXPOSE 8050

CMD ["./start.sh", "--env", "--transport", "sse", "--port", "8050"]
