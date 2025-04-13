import os
import threading
import time
from flask import Flask, jsonify, request
from loguru import logger
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(sys.stderr, level=log_level)
logger.add("viewer_bot.log", rotation="10 MB", level="DEBUG")

# Check if proxy scanning is enabled
scan_proxies = os.getenv("SCAN_PROXIES", "true").lower() == "true"

# Create Flask app
app = Flask(__name__)

# Global variables to track bot status
bot_status = {
    "is_running": False,
    "total_bots": 0,
    "active_bots": 0,
    "completed_views": 0,
    "start_time": None,
    "last_update": None
}

@app.route('/')
def home():
    """Home page with status information."""
    global bot_status
    
    # Calculate uptime if the bot has started
    uptime = ""
    if bot_status["start_time"]:
        uptime_seconds = int(time.time() - bot_status["start_time"])
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{hours}h {minutes}m {seconds}s"
    
    return jsonify({
        "status": "running" if bot_status["is_running"] else "idle",
        "total_bots": bot_status["total_bots"],
        "active_bots": bot_status["active_bots"],
        "completed_views": bot_status["completed_views"],
        "uptime": uptime,
        "last_update": bot_status["last_update"]
    })

@app.route('/proxies')
def get_proxies():
    """Display the list of working proxies."""
    try:
        if os.path.exists("working_proxies.txt"):
            with open("working_proxies.txt", "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            return jsonify({
                "count": len(proxies),
                "proxies": proxies
            })
        else:
            return jsonify({
                "error": "No working proxies file found",
                "count": 0,
                "proxies": []
            })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "count": 0,
            "proxies": []
        })

@app.route('/test-proxies')
def test_proxies_endpoint():
    """Test proxies with time limit."""
    # Check if proxy scanning is disabled
    scan_proxies = os.getenv("SCAN_PROXIES", "true").lower() == "true"
    if not scan_proxies:
        if os.path.exists("working_proxies.txt"):
            with open("working_proxies.txt", "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            return jsonify({
                "status": "skipped", 
                "message": f"Proxy scanning disabled, using {len(proxies)} existing proxies",
                "count": len(proxies)
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Proxy scanning disabled but no existing proxies found",
                "count": 0
            })
    
    # Get time limit from query parameter or use default (20 minutes)
    time_limit = request.args.get('time_limit', default=1200, type=int)
    
    if bot_status["is_running"]:
        return jsonify({"status": "error", "message": "Bot system is already running"})
    
    # Start proxy testing in a background thread
    thread = threading.Thread(target=run_proxy_testing, args=(time_limit,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "status": "started", 
        "message": f"Proxy testing started with {time_limit} second time limit",
        "time_limit": time_limit
    })

def run_proxy_testing(time_limit=1200):
    """Run proxy testing in the background."""
    global bot_status
    
    try:
        # Update status
        bot_status["is_running"] = True
        bot_status["start_time"] = time.time()
        bot_status["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Import the proxy testing modules
        try:
            from proxy_scraper import ProxyScraper
            from proxy_tester import main as test_proxies
        except ImportError:
            logger.error("Failed to import proxy modules")
            bot_status["is_running"] = False
            return
        
        # Scrape proxies
        logger.info("Scraping proxies from various sources...")
        scraper = ProxyScraper()
        proxies = scraper.scrape_all_sources()
        
        if proxies:
            scraper.save_to_file()
            
            # Test proxies with time limit
            logger.info(f"Testing proxies with {time_limit} second time limit...")
            bot_status["active_bots"] = 1  # Show as active
            test_proxies(time_limit)
            
            # Check results
            if os.path.exists("working_proxies.txt"):
                with open("working_proxies.txt", "r") as f:
                    working_proxies = [line.strip() for line in f if line.strip()]
                logger.success(f"Found {len(working_proxies)} working proxies")
                bot_status["completed_views"] = len(working_proxies)
            else:
                logger.warning("No working proxies found")
        else:
            logger.error("Failed to scrape any proxies")
        
    except Exception as e:
        logger.error(f"Error testing proxies: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        # Update status
        bot_status["is_running"] = False
        bot_status["active_bots"] = 0
        bot_status["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Proxy testing finished")

@app.route('/start')
def start_bots():
    """Start the YouTube viewer bot system."""
    global bot_status
    
    if bot_status["is_running"]:
        return jsonify({"status": "already_running", "message": "Bot system is already running"})
    
    # Reset status
    bot_status["is_running"] = True
    bot_status["total_bots"] = int(os.getenv("NUM_BOTS", 100))
    bot_status["active_bots"] = 0
    bot_status["completed_views"] = 0
    bot_status["start_time"] = time.time()
    bot_status["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Start the bot system in a background thread
    bot_thread = threading.Thread(target=run_bot_system)
    bot_thread.daemon = True
    bot_thread.start()
    
    logger.info("Bot system started via web interface")
    return jsonify({"status": "started", "message": "Bot system started"})

def run_bot_system():
    """Run the YouTube viewer bot system in the background."""
    try:
        # Import the bot system modules
        from main import main as run_main
        
        # Run the bot system
        run_main()
        
    except Exception as e:
        logger.error(f"Error running bot system: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        # Update status
        global bot_status
        bot_status["is_running"] = False
        bot_status["active_bots"] = 0
        bot_status["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Bot system finished")

def update_status(active=0, completed=0):
    """Update the bot status information."""
    global bot_status
    bot_status["active_bots"] = active
    bot_status["completed_views"] += completed
    bot_status["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")

# Auto-start the bot on server initialization
def auto_start_bot():
    """Start the bot automatically when the server starts."""
    if not bot_status["is_running"]:
        logger.info("Auto-starting bot system")
        start_bots()

# Initialize the application with the auto-start
with app.app_context():
    auto_start_bot()

if __name__ == "__main__":
    # Get port from environment variable for Render compatibility
    port = int(os.environ.get("PORT", 5000))
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=port) 