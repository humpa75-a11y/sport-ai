"""
🔍 TOTO API EXPLORER - Find the Football Events Endpoint
===========================================================
TOTO uses different API structure than Kambi bookmakers
Need to find the actual events/odds endpoints
"""

import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class TOTOAPIExplorer:
    """Explore TOTO API to find football events"""
    
    def __init__(self):
        self.base_url = "https://sport-api.toto.nl"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'nl-NL,nl;q=0.9',
            'Origin': 'https://sport.toto.nl',
            'Referer': 'https://sport.toto.nl/wedden/11/voetbal/wedstrijden'
        })
    
    def try_endpoint(self, path: str, params: dict = None) -> dict:
        """Try an API endpoint and return response"""
        try:
            url = f"{self.base_url}{path}"
            logger.info(f"🔍 Trying: {url}")
            if params:
                logger.info(f"   Params: {params}")
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ SUCCESS! Size: {len(str(data))} bytes")
                return {'success': True, 'data': data, 'url': url}
            else:
                logger.info(f"❌ Status {response.status_code}")
                return {'success': False, 'status': response.status_code}
                
        except Exception as e:
            logger.info(f"❌ Error: {e}")
            return {'success': False, 'error': str(e)}
    
    def explore_common_endpoints(self):
        """Try common API endpoint patterns"""
        
        logger.info("=" * 80)
        logger.info("🔍 EXPLORING TOTO API ENDPOINTS")
        logger.info("=" * 80)
        
        results = {}
        
        # Common endpoint patterns for sports betting APIs
        endpoints_to_try = [
            # Events/Matches
            "/events",
            "/events/upcoming",
            "/events/live",
            "/events/football",
            "/matches",
            "/matches/upcoming",
            "/fixtures",
            "/fixtures/football",
            
            # Sports/Categories
            "/sports",
            "/sports/11",  # 11 is often football
            "/sports/football",
            "/sports/soccer",
            "/categories",
            "/categories/11",
            
            # Competitions
            "/competitions",
            "/competitions/football",
            "/leagues",
            
            # Odds/Markets
            "/odds",
            "/markets",
            "/betting",
            
            # Time-based
            "/today",
            "/this-week",
            "/upcoming",
            
            # Specific paths seen in CMS
            "/sport/11",
            "/sport/football",
            "/sport/voetbal",
            
            # API v1/v2
            "/api/events",
            "/api/sports",
            "/api/v1/events",
            "/api/v2/events",
            "/v1/events",
            "/v2/events",
            
            # Live/Pre-match
            "/prematch",
            "/prematch/events",
            "/live/events",
            "/inplay",
            
            # Feed/Data
            "/feed",
            "/feed/events",
            "/data",
            "/data/events"
        ]
        
        for endpoint in endpoints_to_try:
            result = self.try_endpoint(endpoint)
            if result['success']:
                results[endpoint] = result
                
                # Save successful response
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/toto_explore_{endpoint.replace('/', '_')}_{timestamp}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(result['data'], f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Saved to: {filename}")
        
        # Try with common query parameters
        logger.info("\n" + "=" * 80)
        logger.info("🔍 TRYING WITH QUERY PARAMETERS")
        logger.info("=" * 80)
        
        base_paths = ["/events", "/matches", "/sports", ""]
        param_combinations = [
            {'sport': '11'},
            {'sport': 'football'},
            {'sportId': '11'},
            {'categoryId': '11'},
            {'type': 'football'},
            {'filter': 'football'},
            {'upcoming': 'true'},
            {'live': 'false'}
        ]
        
        for base in base_paths:
            for params in param_combinations:
                result = self.try_endpoint(base, params)
                if result['success']:
                    key = f"{base}?{params}"
                    results[key] = result
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    param_str = "_".join(f"{k}_{v}" for k, v in params.items())
                    filename = f"data/toto_explore_{base.replace('/', '_')}_{param_str}_{timestamp}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result['data'], f, indent=2, ensure_ascii=False)
                    logger.info(f"💾 Saved to: {filename}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 EXPLORATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total endpoints tried: {len(endpoints_to_try) + len(base_paths) * len(param_combinations)}")
        logger.info(f"Successful endpoints: {len(results)}")
        
        if results:
            logger.info("\n✅ WORKING ENDPOINTS:")
            for endpoint, data in results.items():
                logger.info(f"   → {endpoint}")
        else:
            logger.info("\n❌ No additional endpoints found")
            logger.info("   TOTO may use dynamic/authenticated endpoints")
            logger.info("   Or SignalR real-time connection")
        
        return results


def main():
    explorer = TOTOAPIExplorer()
    results = explorer.explore_common_endpoints()
    
    print("\n" + "=" * 80)
    print("🎯 NEXT STEPS")
    print("=" * 80)
    
    if results:
        print("✅ Found working endpoints!")
        print("   → Check saved JSON files for structure")
        print("   → Build scraper based on discovered structure")
    else:
        print("⚠️ TOTO API requires different approach:")
        print("   1. SignalR real-time connection (complex)")
        print("   2. Browser automation with API interception")
        print("   3. Focus on Unibet + Jacks (already working)")
        print("\n💡 RECOMMENDATION:")
        print("   → TOTO data may not be worth the extra complexity")
        print("   → Unibet + Jacks already provide 30+ matches")
        print("   → Both use same Kambi backend = consistent data")
        print("   → Focus on training AI with existing 100% accuracy!")


if __name__ == "__main__":
    main()
