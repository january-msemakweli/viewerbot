# YouTube Viewer Bot

A simple YouTube viewer bot system that simulates multiple viewers watching a YouTube video using headless browsers and proxy rotation.

**DISCLAIMER**: This project is for educational purposes only. Using bots to artificially inflate YouTube views may violate YouTube's Terms of Service. Use at your own risk.

## Features

- Simulates 28 concurrent viewers (matching our pre-tested working proxies)
- Uses a pre-configured list of working proxies (no scanning needed)
- Rotates IP addresses using proxies to avoid detection
- Randomized viewing durations
- Random user agent rotation
- Headless browser operation (no GUI required)
- Detailed logging system
- Web interface for monitoring

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
4. The system comes with a pre-configured list of 28 working proxies in `working_proxies.txt`

## Usage

### Running Locally

To run the system locally with the default settings:

```bash
python main.py
```

To run just the web server (recommended for better control):

```bash
python server.py
```

Once the server is running, open your browser to:
- `http://localhost:10000` - View bot status
- `http://localhost:10000/proxies` - View working proxies
- `http://localhost:10000/start` - Start the bot system

### Full Process Flow

The system will:
1. Use the pre-configured list of 28 working proxies
2. Start 28 bot instances (one for each proxy)
3. Each bot will watch the video for a random duration
4. Logs will be saved to various log files

## Configuration

You can configure the bot through the `.env` file in the project root with the following parameters:

```
# YouTube Viewer Bot Configuration

# Target YouTube video URL
VIDEO_URL=https://www.youtube.com/watch?v=2oW9zGtnWDA

# Number of bot instances to run simultaneously (matches number of working proxies)
NUM_BOTS=28

# Number of views per bot
VIEWS_PER_BOT=5

# Minimum watch time in seconds
MIN_WATCH_TIME=30

# Maximum watch time in seconds
MAX_WATCH_TIME=180

# Proxy settings
# Set to true to use proxies, false to disable proxy usage
USE_PROXIES=true

# Skip proxy scanning (use existing working_proxies.txt)
SCAN_PROXIES=false

# Chrome driver settings
# Set to true for headless mode (no GUI)
HEADLESS_MODE=true

# Log configuration
LOG_LEVEL=INFO
```

## Deployment on Render

To deploy this project on Render:

1. Create a new Web Service on Render
2. Connect your repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `python server.py`
5. Environment variables will be automatically configured from render.yaml

Note: For Render deployment to work with Chrome/Selenium, you'll need to use their Docker environment with the proper dependencies. The included Dockerfile and render.yaml files are configured for this purpose.

### Render Free Plan Limitations

If using Render's free plan, be aware of these limitations:

- Only 512MB RAM available (can run ~1-3 Chrome instances at a time)
- Limited CPU resources
- Views will still complete but will take longer as bots run in smaller batches

## Files and Structure

- `main.py` - Main entry point and orchestration
- `bot.py` - Core bot functionality for viewing videos
- `server.py` - Web server for status monitoring and control
- `requirements.txt` - Required Python packages
- `.env` - Configuration file for bot settings
- `Dockerfile` - Docker configuration for deployment
- `render.yaml` - Render deployment configuration
- `working_proxies.txt` - Pre-configured list of working proxies

## Troubleshooting

- **Chrome/Selenium issues**: Make sure Chrome is installed and updated.
- **Dependencies**: Ensure all required packages are installed correctly.
- **Configuration**: Check your .env file for correct settings.
- **Resource limitations**: If experiencing memory issues, reduce views_per_bot or add delays between views.

## License

This project is for educational purposes only. 