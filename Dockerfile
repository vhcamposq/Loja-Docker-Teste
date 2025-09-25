# Dockerfile for Loja de Software (Django)

# Base image
FROM python:3.12-slim

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# System packages (minimal, enough for Pillow and SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    libjpeg62-turbo \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (leverage Docker layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy project
# Note: media/ and staticfiles/ are runtime dirs; they will be mounted as volumes
COPY . /app

# Ensure runtime directories exist
RUN mkdir -p /app/media /app/staticfiles

# Expose Django dev server port
EXPOSE 8000

# Entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
