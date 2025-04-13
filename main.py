import os
import sys
import time
from loguru import logger

# Set up logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("viewer_bot.log", rotation="10 MB", level="DEBUG")

logger.info("Starting YouTube Viewer Bot System")

# Import our modules
try:
    from proxy_scraper import ProxyScraper
    from proxy_tester import test_proxy, load_proxies_from_file, save_working_proxies
    from bot import main as run_bots
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.info("Make sure you have installed all required packages from requirements.txt")
    sys.exit(1)

def setup_proxies():
    """Set up and test proxies."""
    # Check if we already have working proxies
    if os.path.exists("working_proxies.txt"):
        proxies = load_proxies_from_file("working_proxies.txt")
        if proxies and len(proxies) >= 20:  # Arbitrary threshold
            logger.info(f"Using {len(proxies)} existing working proxies")
            return True
    
    # Scrape new proxies
    logger.info("Scraping proxies from various sources...")
    scraper = ProxyScraper()
    proxies = scraper.scrape_all_sources()
    
    if not proxies:
        logger.error("Failed to scrape any proxies. Will try to continue without proxies.")
        return False
    
    scraper.save_to_file()
    
    # Test proxies
    logger.info(f"Testing {len(proxies)} proxies...")
    working_proxies = []
    
    # Test each proxy and collect working ones
    for proxy in proxies:
        result_proxy, response_time = test_proxy(proxy)
        if result_proxy:
            working_proxies.append((result_proxy, response_time))
    
    if working_proxies:
        # Sort working proxies by response time
        working_proxies.sort(key=lambda x: x[1])
        save_working_proxies(working_proxies)
        logger.success(f"Found {len(working_proxies)} working proxies")
        return True
    else:
        logger.warning("No working proxies found. Will try to continue without proxies.")
        return False

def main():
    """Main function to run the YouTube viewer bot system."""
    try:
        # Setup phase
        logger.info("Setting up the YouTube viewer bot system...")
        
        # Set up proxies
        has_proxies = setup_proxies()
        if not has_proxies:
            logger.warning("Running without proxies may affect view count validity and could lead to IP blocking")
            confirmation = input("Continue without proxies? (y/n): ")
            if confirmation.lower() != 'y':
                logger.info("Exiting as per user request")
                return
        
        # Get configuration from environment or use defaults
        num_bots = int(os.environ.get("NUM_BOTS", 100))
        views_per_bot = int(os.environ.get("VIEWS_PER_BOT", 5))
        
        # Display configuration
        logger.info(f"Configuration: {num_bots} bots, {views_per_bot} views per bot")
        logger.info(f"Total expected views: {num_bots * views_per_bot}")
        
        # Start the bots
        logger.info("Starting YouTube viewer bots...")
        run_bots(num_bots, views_per_bot)
        
        logger.success("YouTube viewer bot session completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("YouTube viewer bot system shutting down")

if __name__ == "__main__":
    main() 