FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY agentbeats-leaderboard/green-agent/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY a2_bench/ ./a2_bench/
COPY configs/ ./configs/
COPY setup.py .
COPY README.md .
RUN pip install --no-cache-dir -e .

COPY agentbeats-leaderboard/green-agent/server.py .

ENV A2BENCH_DOMAIN=healthcare

EXPOSE 9009

ENTRYPOINT ["python", "server.py"]
CMD ["--host", "0.0.0.0", "--port", "9009"]
