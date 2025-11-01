"""
🥷 STEALTH SCRAPER - Undetected Web Scraping

Zorgt ervoor dat we NIET gedetecteerd worden als bot.
We scrapen rustig, natuurlijk, en blijven onder de radar.

"Rustig aan, bookmakers uitkleden" 😎

Features:
- Random delays tussen requests (2-8 seconden)
- Rotating User-Agents (Chrome, Firefox, Safari)
- Human-like browsing patterns
- Request rate limiting
- Session management
- Referrer spoofing
- Cookie handling

Author: De Meester AI - Stealth Mode
Date: November 2025
"""

import time
import random
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from functools import wraps

logger = logging.getLogger(__name__)


# ============================================
# 🎭 USER AGENT POOL (Real browsers)
# ============================================

USER_AGENTS = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    
    # Chrome on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    
    # Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    
    # Firefox on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0',
    
    # Safari on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    
    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
]


# ============================================
# 🌐 REFERRER POOL (Look natural)
# ============================================

REFERRERS = [
    'https://www.google.com/',
    'https://www.google.nl/',
    'https://www.bing.com/',
    'https://duckduckgo.com/',
    '',  # Direct traffic (no referrer)
]


class StealthScraper:
    """
    Stealth web scraper that acts like a human.
    Slow, steady, undetectable. 🥷
    """
    
    def __init__(self, min_delay=2.0, max_delay=8.0, requests_per_minute=10):
        self.min_delay = min_delay  # Minimum seconds between requests
        self.max_delay = max_delay  # Maximum seconds between requests
        self.requests_per_minute = requests_per_minute
        
        # Track request history
        self.request_history = []
        self.session = requests.Session()
        
        # Session state (cookies, etc.)
        self.cookies = {}
        
        logger.info(f"🥷 Stealth Scraper initialized")
        logger.info(f"   Delay: {min_delay}-{max_delay}s per request")
        logger.info(f"   Rate limit: {requests_per_minute} req/min")
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Generate random but realistic headers"""
        user_agent = random.choice(USER_AGENTS)
        referrer = random.choice(REFERRERS)
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        if referrer:
            headers['Referer'] = referrer
        
        return headers
    
    def _human_delay(self):
        """Wait like a human (random delay)"""
        delay = random.uniform(self.min_delay, self.max_delay)
        
        # Add occasional longer pauses (reading page)
        if random.random() < 0.1:  # 10% chance
            delay += random.uniform(5, 15)  # Extra 5-15 seconds
            logger.info(f"   💤 Taking a reading break... {delay:.1f}s")
        
        logger.debug(f"   ⏳ Waiting {delay:.1f}s before next request")
        time.sleep(delay)
    
    def _check_rate_limit(self):
        """Ensure we don't exceed requests per minute"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)
        
        # Remove old requests
        self.request_history = [
            req_time for req_time in self.request_history 
            if req_time > cutoff
        ]
        
        # Check if we're at limit
        if len(self.request_history) >= self.requests_per_minute:
            # Wait until oldest request expires
            oldest = min(self.request_history)
            wait_until = oldest + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()
            
            if wait_seconds > 0:
                logger.warning(f"   ⚠️ Rate limit reached, waiting {wait_seconds:.1f}s")
                time.sleep(wait_seconds + 1)  # +1 for safety
    
    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Stealth GET request.
        Acts like a human browsing the web.
        """
        # Check rate limit
        self._check_rate_limit()
        
        # Add delay (human-like)
        if self.request_history:  # Not first request
            self._human_delay()
        
        # Get random headers
        headers = self._get_random_headers()
        
        # Merge with custom headers
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        # Add timeout if not specified
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30
        
        # Make request
        logger.info(f"🥷 Stealth request: {url}")
        try:
            response = self.session.get(url, **kwargs)
            
            # Track request
            self.request_history.append(datetime.now())
            
            # Store cookies
            self.cookies.update(response.cookies.get_dict())
            
            logger.info(f"   ✅ Status: {response.status_code}")
            return response
            
        except Exception as e:
            logger.error(f"   ❌ Request failed: {e}")
            raise
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Stealth POST request"""
        self._check_rate_limit()
        
        if self.request_history:
            self._human_delay()
        
        headers = self._get_random_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 30
        
        logger.info(f"🥷 Stealth POST: {url}")
        try:
            response = self.session.post(url, **kwargs)
            self.request_history.append(datetime.now())
            self.cookies.update(response.cookies.get_dict())
            logger.info(f"   ✅ Status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"   ❌ POST failed: {e}")
            raise
    
    def get_session_cookies(self) -> Dict:
        """Get current session cookies"""
        return self.cookies.copy()
    
    def reset_session(self):
        """Reset session (new identity)"""
        logger.info("🔄 Resetting session (new identity)")
        self.session = requests.Session()
        self.cookies = {}
        self.request_history = []


# ============================================
# 🎯 DECORATOR: Rate Limited Function
# ============================================

def rate_limited(calls_per_minute=10):
    """
    Decorator to rate limit any function.
    Usage:
        @rate_limited(calls_per_minute=5)
        def my_function():
            ...
    """
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                logger.debug(f"⏳ Rate limit: waiting {left_to_wait:.1f}s")
                time.sleep(left_to_wait)
            
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        
        return wrapper
    return decorator


# ============================================
# 🌐 SAFE API CALLER (with retry logic)
# ============================================

class SafeAPICaller:
    """
    Wrapper for API calls with retry, backoff, and error handling.
    Perfect for unreliable APIs.
    """
    
    def __init__(self, scraper: StealthScraper):
        self.scraper = scraper
    
    def call_api(self, url: str, max_retries=3, backoff_factor=2.0, **kwargs):
        """
        Call API with exponential backoff retry.
        
        Args:
            url: API endpoint
            max_retries: Max retry attempts
            backoff_factor: Multiply delay by this each retry
            **kwargs: Passed to scraper.get()
        
        Returns:
            Response or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                response = self.scraper.get(url, **kwargs)
                
                if response.status_code == 200:
                    return response
                
                elif response.status_code == 429:  # Too Many Requests
                    wait = backoff_factor ** attempt * 60
                    logger.warning(f"   ⚠️ 429 Rate Limited, waiting {wait:.0f}s")
                    time.sleep(wait)
                
                elif response.status_code >= 500:  # Server error
                    wait = backoff_factor ** attempt * 10
                    logger.warning(f"   ⚠️ Server error {response.status_code}, retry in {wait:.0f}s")
                    time.sleep(wait)
                
                else:
                    logger.error(f"   ❌ HTTP {response.status_code}, giving up")
                    return None
            
            except requests.exceptions.Timeout:
                logger.warning(f"   ⏰ Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(backoff_factor ** attempt * 5)
            
            except requests.exceptions.ConnectionError:
                logger.warning(f"   🔌 Connection error on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(backoff_factor ** attempt * 5)
            
            except Exception as e:
                logger.error(f"   ❌ Unexpected error: {e}")
                return None
        
        logger.error(f"   ❌ All {max_retries} retries failed for {url}")
        return None


# ============================================
# 🎯 GLOBAL INSTANCE
# ============================================

_scraper = None

def get_stealth_scraper(min_delay=3.0, max_delay=7.0, requests_per_minute=8) -> StealthScraper:
    """
    Get global stealth scraper instance.
    
    Default settings are VERY conservative:
    - 3-7 second delays (human reading time)
    - Max 8 requests per minute (slow and steady)
    """
    global _scraper
    if _scraper is None:
        _scraper = StealthScraper(
            min_delay=min_delay,
            max_delay=max_delay,
            requests_per_minute=requests_per_minute
        )
    return _scraper


if __name__ == '__main__':
    # Test stealth scraper
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*80)
    print("🥷 STEALTH SCRAPER TEST")
    print("="*80)
    
    scraper = get_stealth_scraper(min_delay=1.0, max_delay=3.0, requests_per_minute=20)
    
    # Test multiple requests
    test_urls = [
        'https://httpbin.org/user-agent',
        'https://httpbin.org/headers',
        'https://httpbin.org/get',
    ]
    
    print("\n📡 Making 3 stealth requests...")
    for i, url in enumerate(test_urls, 1):
        print(f"\n{i}. Requesting: {url}")
        try:
            response = scraper.get(url)
            print(f"   Status: {response.status_code}")
            if i == 1:  # Show first user agent
                import json
                data = json.loads(response.text)
                print(f"   User-Agent: {data.get('user-agent', 'N/A')}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n✅ Test complete!")
    print(f"📊 Total requests: {len(scraper.request_history)}")
    print(f"🍪 Cookies stored: {len(scraper.cookies)}")
