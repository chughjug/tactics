# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Avoid prompts during apt installations
ENV DEBIAN_FRONTEND=noninteractive

# Update apt, install python, pip, and compilation requirements for lc0
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    g++ \
    ninja-build \
    python3-dev \
    git \
    meson \
    wget \
    curl \
    pkg-config \
    unzip \
    libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Install lc0 from GitHub releases (since it's not natively in the jammy repository)
WORKDIR /opt
RUN wget https://github.com/LeelaChessZero/lc0/releases/download/v0.31.2/lc0-v0.31.2-linux-cpu-openblas.tar.gz && \
    tar -xzvf lc0-v0.31.2-linux-cpu-openblas.tar.gz && \
    cp lc0-v0.31.2-linux-cpu-openblas/lc0 /usr/local/bin/ && \
    chmod +x /usr/local/bin/lc0 && \
    rm -rf lc0*

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
