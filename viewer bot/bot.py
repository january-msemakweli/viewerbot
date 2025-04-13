import os
import time
import random
import threading
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import undetected_chromedriver as uc
from loguru import logger

# Configure logger
logger.add("bot_log.log", rotation="10 MB")

# YouTube video URL
VIDEO_URL = "https://www.youtube.com/watch?v=2oW9zGtnWDA"

# List of free proxies (you can update this list or use a proxy service API)
PROXIES = []

# Load proxies from working_proxies.txt if it exists
if os.path.exists("working_proxies.txt"):
    try:
        with open("working_proxies.txt", "r") as f:
            PROXIES = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(PROXIES)} proxies from working_proxies.txt")
    except Exception as e:
        logger.error(f"Error loading proxies from file: {e}")

# Use free-proxy package to get proxies if the list is empty
if not PROXIES:
    try:
        from fp.fp import FreeProxy
        for _ in range(150):  # Try to get more proxies than needed in case some fail
            try:
                proxy = FreeProxy(rand=True).get()
                if proxy and proxy not in PROXIES:
                    PROXIES.append(proxy)
            except Exception as e:
                logger.error(f"Error fetching proxy: {e}")
                time.sleep(1)
    except ImportError:
        logger.warning("free-proxy package not installed, using direct connections")

# Randomized watch times (between 30 seconds and full video length)
MIN_WATCH_TIME = 30  # seconds
MAX_WATCH_TIME = 180  # seconds (adjust based on video length)

# Generate random user agents
user_agent = UserAgent()

def get_webdriver(proxy=None):
    """Create and return a webdriver instance with optional proxy settings."""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--mute-audio")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        
        # Run in headless mode (no GUI)
        options.add_argument("--headless")
        
        # Set random user agent
        options.add_argument(f"--user-agent={user_agent.random}")
        
        # Add proxy if provided
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        
        # Initialize Chrome driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        logger.error(f"Error creating webdriver: {e}")
        return None

def view_video(bot_id, proxy=None):
    """Function to view the YouTube video with a specific bot ID and optional proxy."""
    driver = None
    try:
        logger.info(f"Bot #{bot_id} starting with proxy: {proxy or 'None'}")
        
        # Create webdriver with proxy if available
        driver = get_webdriver(proxy)
        if not driver:
            logger.error(f"Bot #{bot_id} failed to create webdriver")
            return
        
        # Open video URL
        driver.get(VIDEO_URL)
        logger.info(f"Bot #{bot_id} opened video page")
        
        # Wait for video player to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "video"))
            )
            logger.info(f"Bot #{bot_id} video player loaded")
        except TimeoutException:
            logger.warning(f"Bot #{bot_id} timeout waiting for video player")
            return
        
        # Check if video is playing (optional)
        try:
            # Try to click play button if video is not auto-playing
            play_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-play-button"))
            )
            
            if "Play" in play_button.get_attribute("aria-label"):
                play_button.click()
                logger.info(f"Bot #{bot_id} clicked play button")
        except Exception as e:
            logger.warning(f"Bot #{bot_id} play button interaction error: {e}")
        
        # Determine random watch time
        watch_time = random.randint(MIN_WATCH_TIME, MAX_WATCH_TIME)
        logger.info(f"Bot #{bot_id} watching for {watch_time} seconds")
        
        # Wait for the determined watch time
        time.sleep(watch_time)
        
        logger.success(f"Bot #{bot_id} successfully watched video for {watch_time} seconds")
        
    except WebDriverException as e:
        logger.error(f"Bot #{bot_id} WebDriver error: {e}")
    except Exception as e:
        logger.error(f"Bot #{bot_id} unexpected error: {e}")
    finally:
        # Close the browser
        if driver:
            try:
                driver.quit()
                logger.info(f"Bot #{bot_id} browser closed")
            except Exception as e:
                logger.error(f"Bot #{bot_id} error closing browser: {e}")

def bot_cycle(bot_id, num_views=5):
    """Run a bot through multiple view cycles."""
    for view_count in range(1, num_views + 1):
        # Choose a random proxy or None
        proxy = random.choice(PROXIES) if PROXIES else None
        
        logger.info(f"Bot #{bot_id} starting view #{view_count}/{num_views}")
        view_video(bot_id, proxy)
        
        # Random delay between views (1-5 minutes)
        if view_count < num_views:
            delay = random.randint(10, 30)
            logger.info(f"Bot #{bot_id} waiting {delay} seconds before next view")
            time.sleep(delay)

def main(num_bots=100, views_per_bot=5):
    """Run multiple bots concurrently."""
    logger.info(f"Starting {num_bots} bots with {views_per_bot} views each")
    
    # Create and start bot threads
    threads = []
    for bot_id in range(1, num_bots + 1):
        t = threading.Thread(target=bot_cycle, args=(bot_id, views_per_bot))
        threads.append(t)
        t.start()
        
        # Add a small delay between starting bots to avoid overwhelming resources
        time.sleep(random.uniform(1, 3))
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    logger.success(f"All {num_bots} bots completed their cycles")

if __name__ == "__main__":
    # Default configuration
    num_bots = 100
    views_per_bot = 5
    
    # You can override defaults with environment variables
    if os.environ.get("NUM_BOTS"):
        num_bots = int(os.environ.get("NUM_BOTS"))
    if os.environ.get("VIEWS_PER_BOT"):
        views_per_bot = int(os.environ.get("VIEWS_PER_BOT"))
    
    main(num_bots, views_per_bot) 