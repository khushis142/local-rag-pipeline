FROM python:3.12-slim

WORKDIR /app

# Install Java Runtime (Required for Apache Spark Processing Engine)
RUN apt-get update && \
    apt-get install -y default-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

CMD ["tail", "-f", "/dev/null"]