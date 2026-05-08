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
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone and build lc0 from source
WORKDIR /opt
RUN git clone -b v0.32.1 --recurse-submodules https://github.com/LeelaChessZero/lc0.git && \
    cd lc0 && \
    ./build.sh && \
    cp build/release/lc0 /usr/local/bin/ && \
    cd /opt && \
    rm -rf lc0

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
