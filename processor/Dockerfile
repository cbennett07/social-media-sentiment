FROM python:3.12-slim

WORKDIR /app

# Install postgres client libraries and curl for health checks
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-processor.txt .
RUN pip install --no-cache-dir -r requirements-processor.txt

COPY . .

EXPOSE 8081

# Default to API mode, override with "worker" for continuous processing
CMD ["python", "-m", "processor.main"]
