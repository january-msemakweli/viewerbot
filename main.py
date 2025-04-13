import os
import sys
import time
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(sys.stderr, level=log_level)
logger.add("viewer_bot.log", rotation="10 MB", level="DEBUG")

logger.info("Starting YouTube Viewer Bot System")

# Check if proxy scanning is enabled
scan_proxies = os.getenv("SCAN_PROXIES", "true").lower() == "true"

# Import our modules
try:
    # Import bot module (always needed)
    from bot import main as run_bots
    
    # Only import proxy-related modules if needed
    if scan_proxies:
        try:
            from proxy_scraper import ProxyScraper
            from proxy_tester import test_proxy, load_proxies_from_file, save_working_proxies, main as test_proxies
        except ImportError as e:
            if scan_proxies:
                logger.error(f"Failed to import proxy modules: {e}")
                logger.warning("Continuing without proxy scanning capability")
                scan_proxies = False
    else:
        # Define minimal functions for when scan_proxies is disabled
        def load_proxies_from_file(filename="working_proxies.txt"):
            try:
                with open(filename, "r") as f:
                    proxies = [line.strip() for line in f if line.strip()]
                logger.info(f"Loaded {len(proxies)} proxies from {filename}")
                return proxies
            except Exception as e:
                logger.error(f"Error loading proxies from file: {e}")
                return []
    
    # Try to import the status updater from server.py, but don't fail if it's not there
    try:
        from server import update_status
    except ImportError:
        # Create a dummy update_status function if server.py is not available
        def update_status(active=0, completed=0):
            pass
            
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.info("Make sure you have installed all required packages from requirements.txt")
    sys.exit(1)

def setup_proxies(time_limit=1200):  # Default 20 minutes
    """Set up and test proxies with a time limit."""
    # Check if proxy usage is disabled
    use_proxies = os.getenv("USE_PROXIES", "true").lower() == "true"
    if not use_proxies:
        logger.info("Proxy usage disabled in configuration")
        return False
    
    # Check if proxy scanning should be skipped
    scan_proxies = os.getenv("SCAN_PROXIES", "true").lower() == "true"
    
    # Check if we already have working proxies
    if os.path.exists("working_proxies.txt"):
        proxies = load_proxies_from_file("working_proxies.txt")
        if proxies:
            logger.info(f"Using {len(proxies)} existing working proxies")
            if not scan_proxies:
                logger.info("Proxy scanning disabled, using existing proxy list")
                return True
            elif len(proxies) >= 20:  # Arbitrary threshold
                logger.info(f"Found sufficient proxies ({len(proxies)}), skipping scanning")
                return True
    
    # If proxy scanning is disabled but no working proxies exist, warn and continue
    if not scan_proxies:
        if not os.path.exists("working_proxies.txt") or not load_proxies_from_file("working_proxies.txt"):
            logger.warning("Proxy scanning disabled but no working proxies found. Will try to continue without proxies.")
            return False
        return True
    
    # If we reach here, we need to scan for proxies
    if not 'ProxyScraper' in globals():
        logger.error("Proxy scanning required but proxy modules are not available")
        return False
    
    # Scrape new proxies
    logger.info("Scraping proxies from various sources...")
    scraper = ProxyScraper()
    proxies = scraper.scrape_all_sources()
    
    if not proxies:
        logger.error("Failed to scrape any proxies. Will try to continue without proxies.")
        return False
    
    scraper.save_to_file()
    
    # Test proxies with time limit
    logger.info(f"Testing proxies with {time_limit} second time limit...")
    
    # Update status to show we're testing proxies
    update_status(active=1)
    
    # Use the time-limited testing function
    # This will save working_proxies.txt directly
    test_proxies(time_limit)
    
    # Update status to show we're done testing proxies
    update_status(active=0)
    
    # Check if we found any working proxies
    if os.path.exists("working_proxies.txt"):
        working_proxies = load_proxies_from_file("working_proxies.txt")
        if working_proxies:
            logger.success(f"Found {len(working_proxies)} working proxies")
            return True
    
    logger.warning("No working proxies found. Will try to continue without proxies.")
    return False

def main():
    """Main function to run the YouTube viewer bot system."""
    try:
        # Setup phase
        logger.info("Setting up the YouTube viewer bot system...")
        
        # Get proxy testing time limit from environment or use default (20 minutes)
        proxy_test_time_limit = int(os.getenv("PROXY_TEST_TIME_LIMIT", 1200))
        
        # Set up proxies if enabled
        use_proxies = os.getenv("USE_PROXIES", "true").lower() == "true"
        has_proxies = False
        
        if use_proxies:
            has_proxies = setup_proxies(time_limit=proxy_test_time_limit)
            if not has_proxies:
                logger.warning("Running without proxies may affect view count validity and could lead to IP blocking")
                # When running in headless mode or on Render, we'll continue without proxies
                if os.getenv("HEADLESS_MODE", "true").lower() == "true":
                    logger.info("Continuing without proxies in headless mode")
                else:
                    confirmation = input("Continue without proxies? (y/n): ")
                    if confirmation.lower() != 'y':
                        logger.info("Exiting as per user request")
                        return
        else:
            logger.info("Proxy usage disabled in configuration")
        
        # Get configuration from environment variables
        num_bots = int(os.getenv("NUM_BOTS", 100))
        views_per_bot = int(os.getenv("VIEWS_PER_BOT", 5))
        
        # Display configuration
        logger.info(f"Configuration: {num_bots} bots, {views_per_bot} views per bot")
        logger.info(f"Total expected views: {num_bots * views_per_bot}")
        
        # Update status to show we're starting bots
        update_status(active=num_bots)
        
        # Start the bots
        logger.info("Starting YouTube viewer bots...")
        run_bots(num_bots, views_per_bot)
        
        # Update status to show we've completed
        update_status(active=0, completed=num_bots * views_per_bot)
        
        logger.success("YouTube viewer bot session completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Ensure status is updated even if an error occurs
        update_status(active=0)
        logger.info("YouTube viewer bot system shutting down")

if __name__ == "__main__":
    main() 