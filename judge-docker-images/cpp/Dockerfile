FROM python:3.12-slim

# Install GCC + time
RUN apt-get update && apt-get install -y g++ time && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
