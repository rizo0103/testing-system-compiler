# Use GCC base image
FROM gcc:12

# Install Python + pip + Flask + GNU time
RUN apt-get update && apt-get install -y python3 python3-pip time && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Expose Cloud Run default port
EXPOSE 8080

# Run Flask app
CMD ["python3", "app.py"]
