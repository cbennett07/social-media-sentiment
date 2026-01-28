FROM python:3.12-slim

WORKDIR /app

# Install postgres client libraries and curl for health checks
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY . .

EXPOSE 8082

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8082"]
