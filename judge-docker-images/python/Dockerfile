FROM python:3.11-slim

# Install GNU time
RUN apt-get update && apt-get install -y time && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy app files
COPY runner.py app.py requirements.txt ./

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on
EXPOSE 8080

# Start the app
CMD ["python", "app.py"]
