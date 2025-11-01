"""
🕵️ UNIBET API FINDER 🕵️
Ontdek de ECHTE API endpoints die Unibet gebruikt

Strategy:
1. Bezoek Unibet site met browser
2. Monitor network requests
3. Find API calls
4. Extract endpoints
5. Test them
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_unibet_api():
    """Find real Unibet API endpoints"""
    logger.info("🕵️ Starting API discovery...")
    
    # Setup Chrome
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Enable performance logging to catch network requests
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        logger.info("📡 Loading Unibet.nl...")
        driver.get("https://www.unibet.nl/betting/sports/filter/football/all/matches")
        
        # Wait for page to load and make API calls
        time.sleep(10)
        
        logger.info("🔍 Analyzing network requests...")
        
        # Get performance logs
        logs = driver.get_log('performance')
        
        api_endpoints = set()
        
        for log in logs:
            try:
                message = json.loads(log['message'])['message']
                
                if message['method'] == 'Network.requestWillBeSent':
                    url = message['params']['request']['url']
                    
                    # Look for API calls
                    if any(keyword in url.lower() for keyword in ['api', 'offering', 'kambi', 'betoffer', 'event']):
                        api_endpoints.add(url)
                        logger.info(f"🎯 Found API: {url}")
            
            except:
                continue
        
        # Save found endpoints
        if api_endpoints:
            logger.info(f"\n✅ Found {len(api_endpoints)} API endpoints!")
            
            with open('unibet_api_endpoints.txt', 'w') as f:
                for endpoint in sorted(api_endpoints):
                    f.write(endpoint + '\n')
                    print(f"  {endpoint}")
            
            logger.info("\n💾 Saved to: unibet_api_endpoints.txt")
        else:
            logger.warning("⚠️ No API endpoints found")
        
        return list(api_endpoints)
    
    finally:
        driver.quit()


if __name__ == '__main__':
    print("="*80)
    print("🕵️ UNIBET API FINDER")
    print("="*80)
    
    try:
        endpoints = find_unibet_api()
        
        if endpoints:
            print(f"\n✅ SUCCESS! Found {len(endpoints)} API endpoints!")
            print("\nUse these in your scraper:")
            for e in endpoints[:5]:  # Show first 5
                print(f"  {e}")
        else:
            print("\n⚠️ No endpoints found")
            print("Unibet might be using different architecture now")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
