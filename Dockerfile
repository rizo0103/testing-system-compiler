# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    g++ \
    gcc \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Install Python dependencies (assuming your requirements.txt exists)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code into the container
COPY . .

# Expose the port your server runs on
EXPOSE 2040  
# Change if your server runs on a different port

# Define the entry point to run your Python server
CMD ["python", "server.py"]
