import requests
import concurrent.futures
import time
from loguru import logger

logger.add("proxy_test_log.log", rotation="10 MB")

# Maximum time (in seconds) to wait for a proxy to respond
TIMEOUT = 10

# Maximum time (in seconds) to spend testing all proxies
MAX_TESTING_TIME = 1200  # 20 minutes

# Test URL (should be accessible worldwide)
TEST_URL = "https://www.google.com"

def test_proxy(proxy):
    """Test if a proxy is working by making a request to the test URL."""
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    
    try:
        start_time = time.time()
        response = requests.get(
            TEST_URL, 
            proxies=proxies, 
            timeout=TIMEOUT, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            logger.success(f"Proxy {proxy} working, response time: {response_time:.2f}s")
            return proxy, response_time
        else:
            logger.warning(f"Proxy {proxy} returned status code {response.status_code}")
            return None, None
    except requests.exceptions.RequestException as e:
        logger.error(f"Proxy {proxy} failed: {str(e)}")
        return None, None

def load_proxies_from_file(filename="proxies.txt"):
    """Load proxies from a file."""
    try:
        with open(filename, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        logger.info(f"Loaded {len(proxies)} proxies from {filename}")
        return proxies
    except Exception as e:
        logger.error(f"Error loading proxies from file: {e}")
        return []

def save_working_proxies(working_proxies, filename="working_proxies.txt"):
    """Save working proxies to a file."""
    try:
        with open(filename, "w") as f:
            for proxy, response_time in working_proxies:
                f.write(f"{proxy}\n")
        logger.info(f"Saved {len(working_proxies)} working proxies to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving working proxies to file: {e}")
        return False

def main(time_limit=MAX_TESTING_TIME):
    """
    Test proxies with a time limit.
    
    Args:
        time_limit: Maximum time (in seconds) to spend testing proxies.
    """
    # Load proxies from file
    proxies = load_proxies_from_file()
    
    if not proxies:
        logger.error("No proxies found to test.")
        return
    
    logger.info(f"Testing proxies with {time_limit} second time limit...")
    
    # Start timing
    start_time = time.time()
    
    # Test proxies concurrently
    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                result_proxy, response_time = future.result()
                if result_proxy:
                    working_proxies.append((result_proxy, response_time))
            except Exception as e:
                logger.error(f"Error processing proxy {proxy}: {e}")
                
            # Check if we've reached the time limit
            elapsed_time = time.time() - start_time
            if elapsed_time >= time_limit:
                logger.warning(f"Time limit of {time_limit} seconds reached. Stopping proxy testing.")
                # Cancel remaining futures
                for f in list(future_to_proxy.keys()):
                    if not f.done():
                        f.cancel()
                break
    
    # Calculate how many proxies were actually tested
    elapsed_time = time.time() - start_time
    tested_count = sum(1 for f in future_to_proxy.keys() if f.done() and not f.cancelled())
    
    # Sort working proxies by response time
    working_proxies.sort(key=lambda x: x[1])
    
    # Save working proxies to file
    if working_proxies:
        save_working_proxies(working_proxies)
        logger.success(f"Found {len(working_proxies)} working proxies out of {tested_count} tested in {elapsed_time:.2f} seconds.")
    else:
        logger.warning(f"No working proxies found after testing {tested_count} proxies in {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main() 