FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    smartmontools \
    && rm -rf /var/lib/apt/lists/*

# Download and install HD Sentinel Linux CLI
WORKDIR /tmp
RUN wget https://www.hdsentinel.com/hdslin/hdsentinel-020b-x64.zip && \
    unzip hdsentinel-020b-x64.zip && \
    chmod +x HDSentinel && \
    mv HDSentinel /usr/local/bin/ && \
    rm -rf /tmp/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Expose port 30969
EXPOSE 30969

# Run the application
CMD ["python", "app.py"]
