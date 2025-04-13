# YouTube Viewer Bot

A simple YouTube viewer bot system that simulates multiple viewers watching a YouTube video using headless browsers and proxy rotation.

**DISCLAIMER**: This project is for educational purposes only. Using bots to artificially inflate YouTube views may violate YouTube's Terms of Service. Use at your own risk.

## Features

- Simulates up to 100 concurrent viewers (configurable)
- Automatically scrapes and tests free proxies from multiple sources
- Rotates IP addresses using proxies to avoid detection
- Randomized viewing durations
- Random user agent rotation
- Headless browser operation (no GUI required)
- Detailed logging system

## Requirements

- Python 3.8+
- Chrome browser installed
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository or download the files
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```

3. Ensure you have Chrome browser installed on your system
4. Configure your settings in the `.env` file (see Configuration section)

## Usage

1. Run the main script:

```bash
python main.py
```

2. The script will:
   - Scrape and test proxies (if needed and enabled)
   - Start the specified number of bot instances
   - Each bot will watch the video for a random duration
   - Logs will be saved to various log files

### Configuration

You can configure the bot in two ways:

#### 1. Using .env file (recommended)

Create a `.env` file in the project root with the following parameters:

```
# YouTube Viewer Bot Configuration

# Target YouTube video URL
VIDEO_URL=https://www.youtube.com/watch?v=2oW9zGtnWDA

# Number of bot instances to run simultaneously
NUM_BOTS=100

# Number of views per bot
VIEWS_PER_BOT=5

# Minimum watch time in seconds
MIN_WATCH_TIME=30

# Maximum watch time in seconds
MAX_WATCH_TIME=180

# Proxy settings
# Set to true to use proxies, false to disable proxy usage
USE_PROXIES=true

# Chrome driver settings
# Set to true for headless mode (no GUI)
HEADLESS_MODE=true

# Log configuration
LOG_LEVEL=INFO
```

#### 2. Using environment variables

You can also configure the bot using environment variables:

```bash
# To run with 50 bots, each viewing the video 10 times
NUM_BOTS=50 VIEWS_PER_BOT=10 python main.py

# To disable proxy usage
USE_PROXIES=false python main.py

# To use non-headless mode (shows browser windows)
HEADLESS_MODE=false python main.py
```

## Deployment on Render

To deploy this project on Render:

1. Create a new Web Service on Render
2. Connect your repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `python main.py`
5. Add environment variables if needed (NUM_BOTS, VIEWS_PER_BOT, etc.)
6. Set the Docker build environment for Chrome support

Note: For Render deployment to work with Chrome/Selenium, you'll need to use their Docker environment with the proper dependencies. The included Dockerfile and render.yaml files are configured for this purpose.

## Files and Structure

- `main.py` - Main entry point and orchestration
- `bot.py` - Core bot functionality for viewing videos
- `proxy_scraper.py` - Scrapes free proxies from various sources
- `proxy_tester.py` - Tests proxies for availability and speed
- `requirements.txt` - Required Python packages
- `.env` - Configuration file for bot settings
- `Dockerfile` - Docker configuration for deployment
- `render.yaml` - Render deployment configuration

## Troubleshooting

- **No proxies found**: The bot will ask if you want to continue without proxies. This may affect view count validity.
- **Chrome/Selenium issues**: Make sure Chrome is installed and updated.
- **Dependencies**: Ensure all required packages are installed correctly.
- **Configuration**: Check your .env file for correct settings.

## License

This project is for educational purposes only. 