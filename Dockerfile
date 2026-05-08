# Use Ubuntu 22.04 as the base image since it has lc0 in its apt repository
FROM ubuntu:22.04

# Avoid prompts during apt installations
ENV DEBIAN_FRONTEND=noninteractive

# Update apt and install Python, pip, and the lc0 chess engine
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    lc0 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirement files first for docker caching
COPY requirements.txt .

# Install python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port (Render sets PORT environment variable, defaults to 5000 in our Gunicorn command)
EXPOSE 5000

# Command to run the application using Gunicorn for production
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} server:app
