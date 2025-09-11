FROM gcc:13.2.0

WORKDIR /app

# Copy runner script
COPY runner.cpp.py /app/runner.py

# Default command runs the runner
CMD ["python3", "runner.py"]