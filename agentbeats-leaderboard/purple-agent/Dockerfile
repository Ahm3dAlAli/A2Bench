FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 9010

ENTRYPOINT ["python", "server.py"]
CMD ["--host", "0.0.0.0", "--port", "9010"]
