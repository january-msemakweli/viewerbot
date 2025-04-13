import requests
import time
import random
from loguru import logger
from bs4 import BeautifulSoup

logger.add("proxy_log.log", rotation="10 MB")

class ProxyScraper:
    def __init__(self):
        self.proxies = []
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
        ]
    
    def get_random_user_agent(self):
        return random.choice(self.user_agents)
    
    def scrape_free_proxy_list(self):
        """Scrape proxies from free-proxy-list.net"""
        try:
            url = "https://free-proxy-list.net/"
            headers = {"User-Agent": self.get_random_user_agent()}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch from {url}, status code: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            proxy_table = soup.find("table", {"id": "proxylisttable"})
            
            if not proxy_table:
                logger.error(f"Could not find proxy table on {url}")
                return []
            
            proxies = []
            for row in proxy_table.tbody.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    ip = cells[0].text
                    port = cells[1].text
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)
                    
            logger.info(f"Scraped {len(proxies)} proxies from free-proxy-list.net")
            return proxies
        except Exception as e:
            logger.error(f"Error scraping free-proxy-list.net: {e}")
            return []
    
    def scrape_geonode(self):
        """Scrape proxies from geonode.com"""
        try:
            url = "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc"
            headers = {"User-Agent": self.get_random_user_agent()}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch from {url}, status code: {response.status_code}")
                return []
            
            data = response.json()
            proxies = []
            
            for proxy_data in data.get("data", []):
                ip = proxy_data.get("ip")
                port = proxy_data.get("port")
                if ip and port:
                    proxy = f"{ip}:{port}"
                    proxies.append(proxy)
            
            logger.info(f"Scraped {len(proxies)} proxies from geonode.com")
            return proxies
        except Exception as e:
            logger.error(f"Error scraping geonode.com: {e}")
            return []
            
    def scrape_proxyscrape(self):
        """Scrape proxies from proxyscrape.com"""
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
            headers = {"User-Agent": self.get_random_user_agent()}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.error(f"Failed to fetch from {url}, status code: {response.status_code}")
                return []
            
            proxy_list = response.text.strip().split("\r\n")
            proxies = [p for p in proxy_list if ":" in p]
            
            logger.info(f"Scraped {len(proxies)} proxies from proxyscrape.com")
            return proxies
        except Exception as e:
            logger.error(f"Error scraping proxyscrape.com: {e}")
            return []
    
    def scrape_all_sources(self):
        """Scrape proxies from all available sources"""
        self.proxies = []
        
        # Add delay between requests to avoid rate limiting
        self.proxies.extend(self.scrape_free_proxy_list())
        time.sleep(2)
        
        self.proxies.extend(self.scrape_geonode())
        time.sleep(2)
        
        self.proxies.extend(self.scrape_proxyscrape())
        
        # Remove duplicates
        self.proxies = list(set(self.proxies))
        
        logger.success(f"Successfully scraped {len(self.proxies)} unique proxies from all sources")
        return self.proxies
    
    def save_to_file(self, filename="proxies.txt"):
        """Save proxies to a file"""
        try:
            with open(filename, "w") as f:
                for proxy in self.proxies:
                    f.write(f"{proxy}\n")
            logger.info(f"Saved {len(self.proxies)} proxies to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving proxies to file: {e}")
            return False

def main():
    scraper = ProxyScraper()
    proxies = scraper.scrape_all_sources()
    
    if proxies:
        scraper.save_to_file()
        logger.info(f"Proxy scraping complete. Found {len(proxies)} proxies.")
    else:
        logger.error("Failed to find any proxies.")

if __name__ == "__main__":
    main() 