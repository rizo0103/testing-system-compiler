FROM python:3.11-slim

# Install GNU time
RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY runner.py app.py ./

RUN pip install flask

CMD ["python", "app.py"]
