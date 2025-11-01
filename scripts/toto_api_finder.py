"""
🎲 TOTO.NL API FINDER
Discover TOTO.nl API voor voetbal wedstrijden

TOTO = grootste Nederlandse bookmaker!
"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_toto_api():
    """Find TOTO.nl API endpoints"""
    
    logger.info("🎲 Starting TOTO.nl API discovery...")
    
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = uc.Chrome(options=options, version_main=136)
    
    try:
        logger.info("🌐 Loading TOTO.nl...")
        driver.get('https://sport.toto.nl/wedden/11/voetbal/wedstrijden')
        
        # Wait for page to load
        logger.info("⏳ Waiting for page to load completely...")
        time.sleep(20)  # Extra tijd voor TOTO
        
        # Try to find some content
        try:
            body_text = driver.find_element(By.TAG_NAME, 'body').text[:500]
            logger.info(f"📄 Page content preview: {body_text[:200]}...")
        except:
            pass
        
        # Get performance logs
        logger.info("📊 Analyzing network traffic...")
        logs = driver.get_log('performance')
        
        api_endpoints = set()
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                method = message.get('message', {}).get('method', '')
                
                if method == 'Network.requestWillBeSent':
                    params = message.get('message', {}).get('params', {})
                    request = params.get('request', {})
                    url = request.get('url', '')
                    
                    # Filter for API calls
                    if any(keyword in url.lower() for keyword in [
                        'api', 'graphql', 'rest', 'data', 'odds', 
                        'sports', 'events', 'matches', 'betting',
                        'soccer', 'football', 'ajax', 'json',
                        'toto', 'wedden', 'voetbal', 'kambi',
                        'sportsbook', 'betoffer'
                    ]):
                        if not any(skip in url.lower() for skip in [
                            'google', 'facebook', 'analytics', 'tag',
                            '.js', '.css', '.png', '.jpg', 'font', '.woff'
                        ]):
                            api_endpoints.add(url)
            
            except Exception as e:
                continue
        
        # Save results
        if api_endpoints:
            logger.info(f"\n✅ Found {len(api_endpoints)} API endpoints!")
            
            with open('data/toto_api_endpoints.txt', 'w', encoding='utf-8') as f:
                for i, endpoint in enumerate(sorted(api_endpoints), 1):
                    f.write(f"{i}. {endpoint}\n")
                    logger.info(f"{i}. {endpoint}")
            
            logger.info(f"\n💾 Saved to: data/toto_api_endpoints.txt")
        else:
            logger.warning("⚠️ No API endpoints found")
        
        # Save page source
        with open('data/toto_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.info("💾 Page source saved to: data/toto_page_source.html")
        
        return list(api_endpoints)
    
    finally:
        driver.quit()


if __name__ == '__main__':
    print("="*80)
    print("🎲 TOTO.NL API FINDER")
    print("="*80)
    
    endpoints = find_toto_api()
    
    if endpoints:
        print(f"\n✅ Found {len(endpoints)} endpoints!")
        print("Check data/toto_api_endpoints.txt for details")
    else:
        print("\n⚠️ No endpoints found - checking page source...")
