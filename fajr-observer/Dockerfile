# Dockerfile — Fajr Observer Agent
# Build: docker build -t fajr-observer .
# Run: docker run --rm --device /dev/video0 fajr-observer --lat 21.5 --lon 39.0 --dry-run

FROM python:3.11-slim

# System deps for OpenCV + ffmpeg
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    ffmpeg \
    mpv \
    && rm -rf /var/lib/apt/lists/*

# Create app dir
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create logs dir
RUN mkdir -p logs/captures logs/images

# Default command (dry-run)
CMD ["python3", "main.py", "--lat", "21.5", "--lon", "39.0", "--dry-run"]
