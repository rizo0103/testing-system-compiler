FROM python:3.12-slim

# Create working directory
WORKDIR /app

# Copy in a runner script that will receive code
COPY runner.py /app/runner.py

# Default command: run the runner
CMD ["python3", "runner.py"]
