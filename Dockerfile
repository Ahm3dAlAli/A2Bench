FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .
RUN pip install --no-cache-dir -e .

# API keys set at runtime
ENV OPENAI_API_KEY=""
ENV ANTHROPIC_API_KEY=""
ENV OPENROUTER_API_KEY=""

# Create results directory
RUN mkdir -p experiments/results/comprehensive

ENTRYPOINT ["python", "experiments/run_comprehensive_multi_domain_evaluation.py"]
CMD ["--models", "gpt-4o", "--domains", "healthcare", "finance", "legal", "--num-seeds", "3"]
