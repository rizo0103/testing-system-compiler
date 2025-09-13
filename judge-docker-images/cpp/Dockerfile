FROM gcc:12

RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY runner.cpp.py /app/runner.py

CMD ["python3", "runner.py"]
