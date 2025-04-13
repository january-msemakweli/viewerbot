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

## Usage

1. Run the main script:

```bash
python main.py
```

2. The script will:
   - Scrape and test proxies (if needed)
   - Start the specified number of bot instances
   - Each bot will watch the video for a random duration
   - Logs will be saved to various log files

### Configuration

You can configure the bot using environment variables:

- `NUM_BOTS`: Number of concurrent bots (default: 100)
- `VIEWS_PER_BOT`: Number of views per bot (default: 5)

Example:

```bash
# To run with 50 bots, each viewing the video 10 times
NUM_BOTS=50 VIEWS_PER_BOT=10 python main.py
```

## Deployment on Render

To deploy this project on Render:

1. Create a new Web Service on Render
2. Connect your repository
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `python main.py`
5. Add environment variables if needed (NUM_BOTS, VIEWS_PER_BOT)
6. Set the Docker build environment for Chrome support

Note: For Render deployment to work with Chrome/Selenium, you'll need to use their Docker environment with the proper dependencies.

## Files and Structure

- `main.py` - Main entry point and orchestration
- `bot.py` - Core bot functionality for viewing videos
- `proxy_scraper.py` - Scrapes free proxies from various sources
- `proxy_tester.py` - Tests proxies for availability and speed
- `requirements.txt` - Required Python packages

## Troubleshooting

- **No proxies found**: The bot will ask if you want to continue without proxies. This may affect view count validity.
- **Chrome/Selenium issues**: Make sure Chrome is installed and updated.
- **Dependencies**: Ensure all required packages are installed correctly.

## License

This project is for educational purposes only. 