FROM python:3.9-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    libgconf-2-4 \
    libxss1 \
    libnss3 \
    libnspr4 \
    libgbm1 \
    libasound2 \
    fonts-liberation

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

# Set up working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files to the container
COPY . .

# Create .env file if not exists with default values
RUN if [ ! -f .env ]; then \
    echo "# YouTube Viewer Bot Configuration" > .env && \
    echo "VIDEO_URL=https://www.youtube.com/watch?v=2oW9zGtnWDA" >> .env && \
    echo "NUM_BOTS=100" >> .env && \
    echo "VIEWS_PER_BOT=5" >> .env && \
    echo "MIN_WATCH_TIME=30" >> .env && \
    echo "MAX_WATCH_TIME=180" >> .env && \
    echo "USE_PROXIES=true" >> .env && \
    echo "HEADLESS_MODE=true" >> .env && \
    echo "LOG_LEVEL=INFO" >> .env; \
    fi

# Environment variables - will override .env if set
ENV NUM_BOTS=100
ENV VIEWS_PER_BOT=5
ENV USE_PROXIES=true
ENV HEADLESS_MODE=true
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# Expose the port the app will run on
EXPOSE ${PORT}

# Command to run when the container starts
CMD ["python", "server.py"] 