"""
🛡️ SCRAPER SAFETY - Whitelist/Blacklist Protection

Zorgt ervoor dat we GEEN Nederlandse bookmakers of verboden sites scrapen.
Wet KOA (Kansspelen op Afstand) compliance.

Author: De Meester AI - Safety First
Date: November 2025
"""

from typing import List, Dict, Set
import logging

logger = logging.getLogger(__name__)


# ============================================
# 🚫 BLACKLIST - NIET SCRAPEN!
# ============================================

BLACKLIST_BOOKMAKERS = {
    # Nederlandse licentiehouders (KOA wet)
    'toto',
    'unibet',
    'betcity',
    'jacks',
    'jacks casino',
    'hollands casino',
    'holland casino',
    'bet365.nl',  # Nederlandse versie
    'napoleongames',
    'circus',
    'bingoal',
    'bet777',
    'bwin',
    'betfirst',
    'supergame',
    'tombola',
    
    # Sites met tracking/profiling
    'sofascore',  # Connected met Bet365
    'flashscore',  # Ook Bet365 linked
}

BLACKLIST_DOMAINS = {
    'toto.nl',
    'unibet.nl',
    'betcity.nl',
    'jackscasino.nl',
    'hollandcasino.nl',
    'bet365.nl',
    'napoleongames.nl',
    'sofascore.com',
    'flashscore.com',
    'flashscore.nl',
}


# ============================================
# ✅ WHITELIST - Veilig om te gebruiken
# ============================================

WHITELIST_BOOKMAKERS = {
    # Internationale sites (geen NL licentie, safe voor data)
    'oddschecker',
    'oddsportal',
    'pinnacle',
    'betfair',  # Exchange, geen direkte bookmaker
    'smarkets',  # Exchange
    'betdaq',  # Exchange
    'bet365.com',  # Internationale versie (NIET .nl)
    'bet365',  # Generic name OK if not .nl domain
    '1xbet',
    '22bet',
    'william hill',
    'ladbrokes',
    'coral',
    'paddy power',
    'betway',
    'marathonbet',
    '10bet',
    '888sport',
    'betvictor',
}

WHITELIST_DOMAINS = {
    'oddschecker.com',
    'oddsportal.com',
    'pinnacle.com',
    'betfair.com',
    'smarkets.com',
    'betdaq.com',
    'bet365.com',  # ALLEEN .com, NIET .nl
    'williamhill.com',
    'ladbrokes.com',
    'coral.co.uk',
    'paddypower.com',
    'betway.com',
    'marathonbet.com',
}


# ============================================
# 🔍 Data sources - Safe analytics sites
# ============================================

SAFE_DATA_SOURCES = {
    # Public stats sites
    'fbref.com',
    'transfermarkt.com',
    'whoscored.com',
    'understat.com',
    'footystats.org',
    'soccerstats.com',
    'football-data.co.uk',
    
    # API services
    'api-football.com',
    'football-data.org',
    'rapidapi.com',
}


class ScraperSafety:
    """Safety checker voor scraper operations"""
    
    def __init__(self):
        self.blacklist_bookmakers = BLACKLIST_BOOKMAKERS
        self.blacklist_domains = BLACKLIST_DOMAINS
        self.whitelist_bookmakers = WHITELIST_BOOKMAKERS
        self.whitelist_domains = WHITELIST_DOMAINS
        self.safe_data_sources = SAFE_DATA_SOURCES
        
        logger.info("🛡️ ScraperSafety initialized")
        logger.info(f"   Blacklisted: {len(self.blacklist_bookmakers)} bookmakers")
        logger.info(f"   Whitelisted: {len(self.whitelist_bookmakers)} bookmakers")
    
    def is_safe_bookmaker(self, name: str) -> bool:
        """Check if bookmaker is safe to scrape"""
        name_lower = name.lower().strip()
        
        # Check blacklist first (highest priority)
        if any(blocked in name_lower for blocked in self.blacklist_bookmakers):
            logger.warning(f"🚫 BLOCKED: {name} is blacklisted!")
            return False
        
        # Special check: Bet365 is OK unless it's .nl
        if 'bet365' in name_lower:
            if '.nl' in name_lower:
                logger.warning(f"🚫 BLOCKED: {name} is Dutch version (.nl)!")
                return False
            else:
                return True  # International bet365 is OK
        
        # Check if whitelisted
        if any(allowed in name_lower for allowed in self.whitelist_bookmakers):
            return True
        
        # If not in either list, default to UNSAFE (better safe than sorry)
        logger.warning(f"⚠️ UNKNOWN: {name} not in whitelist, blocking by default")
        return False
    
    def is_safe_domain(self, url: str) -> bool:
        """Check if domain is safe to scrape"""
        url_lower = url.lower().strip()
        
        # Check blacklist domains
        if any(blocked in url_lower for blocked in self.blacklist_domains):
            logger.warning(f"🚫 BLOCKED: Domain {url} is blacklisted!")
            return False
        
        # Check whitelist domains
        if any(allowed in url_lower for allowed in self.whitelist_domains):
            return True
        
        # Check safe data sources
        if any(source in url_lower for source in self.safe_data_sources):
            return True
        
        # Unknown domain = unsafe
        logger.warning(f"⚠️ UNKNOWN: Domain {url} not in whitelist, blocking")
        return False
    
    def filter_safe_bookmakers(self, bookmaker_list: List[str]) -> List[str]:
        """Filter list to only safe bookmakers"""
        safe = []
        blocked = []
        
        for bookmaker in bookmaker_list:
            if self.is_safe_bookmaker(bookmaker):
                safe.append(bookmaker)
            else:
                blocked.append(bookmaker)
        
        if blocked:
            logger.info(f"🛡️ Filtered out {len(blocked)} blocked bookmakers: {blocked}")
        
        return safe
    
    def filter_safe_urls(self, url_list: List[str]) -> List[str]:
        """Filter list to only safe URLs"""
        safe = []
        blocked = []
        
        for url in url_list:
            if self.is_safe_domain(url):
                safe.append(url)
            else:
                blocked.append(url)
        
        if blocked:
            logger.info(f"🛡️ Filtered out {len(blocked)} blocked URLs")
        
        return safe
    
    def get_betting_warning(self) -> str:
        """Get official warning message"""
        return """
⚠️ VERANTWOORD SPELEN - WAARSCHUWING

Deze AI is bedoeld voor EDUCATIEVE en ANALYTISCHE doeleinden.
Gok NOOIT meer dan je kunt missen.

🇳🇱 Voor Nederlandse gebruikers:
- Gebruik ALLEEN legale bookmakers met KOA licentie
- Maximaal inzet volgens eigen limieten
- Bij verslaving: bel 0800-0160 (Anonieme Gokkers)

📊 Deze AI:
- Scraped GEEN Nederlandse bookmakers
- Gebruikt alleen publieke statistieken
- Geeft geen garanties op winst

Speel verantwoord! 🎯
"""
    
    def check_user_location(self) -> Dict[str, any]:
        """Check if user might be in Netherlands (basic check)"""
        # Simple heuristic - in production use IP geolocation
        return {
            'requires_koa_compliance': True,  # Assume NL for safety
            'allowed_bookmakers': [
                'Toto (voor bets)',
                'Bet365 (internationale versie voor data)',
                'Holland Casino (voor bets)'
            ],
            'warning': self.get_betting_warning()
        }
    
    def get_safe_config(self) -> Dict[str, any]:
        """Get safe scraper configuration"""
        return {
            'allowed_bookmakers': list(self.whitelist_bookmakers),
            'blocked_bookmakers': list(self.blacklist_bookmakers),
            'allowed_domains': list(self.whitelist_domains),
            'blocked_domains': list(self.blacklist_domains),
            'safe_data_sources': list(self.safe_data_sources),
            'recommendation': 'Only use whitelisted sources for odds comparison. Never scrape blacklisted Dutch sites.'
        }


# Global instance
_safety = None

def get_safety() -> ScraperSafety:
    """Get global safety instance"""
    global _safety
    if _safety is None:
        _safety = ScraperSafety()
    return _safety


if __name__ == '__main__':
    # Test safety checker
    safety = ScraperSafety()
    
    print("\n" + "="*80)
    print("🛡️ SCRAPER SAFETY CHECK")
    print("="*80)
    
    # Test bookmakers
    test_bookmakers = [
        'Bet365',
        'Toto',
        'Unibet',
        'Pinnacle',
        'Betcity',
        'Oddschecker',
        'Sofascore',
        'Holland Casino',
        'Betfair Exchange'
    ]
    
    print("\n📊 Bookmaker Safety Check:")
    for bookmaker in test_bookmakers:
        safe = safety.is_safe_bookmaker(bookmaker)
        status = "✅ SAFE" if safe else "🚫 BLOCKED"
        print(f"  {status}: {bookmaker}")
    
    # Test domains
    test_domains = [
        'https://oddschecker.com',
        'https://toto.nl',
        'https://bet365.com',
        'https://bet365.nl',
        'https://sofascore.com',
        'https://pinnacle.com',
        'https://betcity.nl',
        'https://fbref.com'
    ]
    
    print("\n🌐 Domain Safety Check:")
    for domain in test_domains:
        safe = safety.is_safe_domain(domain)
        status = "✅ SAFE" if safe else "🚫 BLOCKED"
        print(f"  {status}: {domain}")
    
    # Print warning
    print("\n" + safety.get_betting_warning())
    
    # Print safe config
    config = safety.get_safe_config()
    print("\n📋 Safe Configuration:")
    print(f"  ✅ Allowed bookmakers: {len(config['allowed_bookmakers'])}")
    print(f"  🚫 Blocked bookmakers: {len(config['blocked_bookmakers'])}")
    print(f"  ✅ Allowed domains: {len(config['allowed_domains'])}")
    print(f"  🚫 Blocked domains: {len(config['blocked_domains'])}")
    print(f"  📊 Safe data sources: {len(config['safe_data_sources'])}")
