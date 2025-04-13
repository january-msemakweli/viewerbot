import os
import threading
import time
from flask import Flask, jsonify
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