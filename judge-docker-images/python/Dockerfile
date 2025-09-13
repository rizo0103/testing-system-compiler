FROM python:3.12-slim

# Install time command for resource usage tracking
RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy in a runner script that will receive code
COPY runner.py /app/runner.py

# Default command: run the runner
CMD ["python3", "runner.py"]
