FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY agentbeats-leaderboard/green-agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy A²-Bench source
COPY a2_bench/ ./a2_bench/
COPY configs/ ./configs/
COPY setup.py .
COPY README.md .
RUN pip install --no-cache-dir -e .

# Copy the A2A server
COPY agentbeats-leaderboard/green-agent/server.py .

EXPOSE 9009

ENTRYPOINT ["python", "server.py"]
CMD ["--host", "0.0.0.0", "--port", "9009"]
