"""
🔥 JACKS.NL COMPLETE SCRAPER 🔥
Scrapes ALLE voetbalwedstrijden met odds van Jacks.nl via Kambi API

Jacks.nl uses SAME backend as Unibet (Kambi)!
So we can reuse the same code structure!
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
from typing import List, Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JacksCompleteScraper:
    """Complete Jacks.nl scraper via Kambi API"""
    
    def __init__(self):
        # JVH = Jacks.nl operator code in Kambi
        self.base_url = "https://eu1.offering-api.kambicdn.com/offering/v2018/jvh"
        self.football_group_id = "1000093190"  # Voetbal group ID (same as Unibet!)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'nl-NL,nl;q=0.9',
            'Referer': 'https://jacks.nl/',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def fetch_all_football_matches(self):
        """Fetch alle voetbalwedstrijden"""
        logger.info("🔍 Fetching all football matches from Jacks.nl...")
        
        # Use betoffer/group endpoint like Unibet
        url = f"{self.base_url}/betoffer/group/{self.football_group_id}.json"
        params = {
            'lang': 'nl_NL',
            'market': 'NL'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ API response received!")
                
                # Save raw data
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                raw_file = f'data/jacks_raw_{timestamp}.json'
                os.makedirs('data', exist_ok=True)
                
                with open(raw_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"💾 Raw data saved: {raw_file}")
                
                # Parse matches
                matches = self.parse_matches(data)
                logger.info(f"🎉 Parsed {len(matches)} matches!")
                
                return matches
            else:
                logger.error(f"❌ API error: {response.status_code}")
                return []
        
        except Exception as e:
            logger.error(f"❌ Exception: {e}")
            return []
    
    def parse_matches(self, data):
        """Parse matches from API response"""
        matches = []
        
        if 'events' not in data:
            logger.warning("No events in response")
            return matches
        
        events = data['events']
        betoffers = {bo['id']: bo for bo in data.get('betOffers', [])}
        
        logger.info(f"📊 Processing {len(events)} events with {len(betoffers)} betoffers...")
        
        for event in events:
            try:
                match = self.parse_single_event(event, betoffers)
                if match:
                    matches.append(match)
            except Exception as e:
                logger.error(f"Error parsing event {event.get('id', 'unknown')}: {e}")
                continue
        
        return matches
    
    def _extract_events_recursive(self, obj, depth=0):
        """Recursively extract events and betoffers from nested structure"""
        if depth > 10:
            return [], {}
        
        events = []
        betoffers = {}
        
        if isinstance(obj, dict):
            # Check if this level has events
            if 'events' in obj and isinstance(obj['events'], list):
                events.extend(obj['events'])
            
            # Check if this level has betOffers
            if 'betOffers' in obj and isinstance(obj['betOffers'], list):
                for bo in obj['betOffers']:
                    betoffers[bo['id']] = bo
            
            # Recurse into all values
            for value in obj.values():
                sub_events, sub_betoffers = self._extract_events_recursive(value, depth+1)
                events.extend(sub_events)
                betoffers.update(sub_betoffers)
        
        elif isinstance(obj, list):
            for item in obj:
                sub_events, sub_betoffers = self._extract_events_recursive(item, depth+1)
                events.extend(sub_events)
                betoffers.update(sub_betoffers)
        
        return events, betoffers
    
    def parse_single_event(self, event, betoffers):
        """Parse een enkele wedstrijd"""
        # Event is already the event data (not nested)
        event_id = event.get('id')
        
        # Get team names - they're directly available!
        home_team = event.get('homeName', '')
        away_team = event.get('awayName', '')
        
        if not home_team or not away_team:
            # Fallback to parsing name
            event_name = event.get('name', '')
            if ' - ' not in event_name:
                return None
            teams = event_name.split(' - ')
            home_team = teams[0].strip()
            away_team = teams[1].strip()
        
        # Start tijd
        start_time = event.get('start')
        
        # League info
        league = event.get('group', 'Unknown')
        
        # Initialize match
        match = {
            'home_team': home_team,
            'away_team': away_team,
            'league': league,
            'start_time': start_time,
            'event_id': event_id,
            'odds_1': None,
            'odds_x': None,
            'odds_2': None,
            'over_2_5': None,
            'under_2_5': None,
            'btts_yes': None,
            'btts_no': None,
            'timestamp': datetime.now().isoformat(),
            'source': 'jacks.nl (Kambi API)'
        }
        
        # Find betoffers for this event
        event_betoffers = [bo for bo in betoffers.values() if bo.get('eventId') == event_id]
        
        for betoffer in event_betoffers:
            criterion = betoffer.get('criterion', {}).get('label', '').lower()
            
            # 1X2 Market
            if any(keyword in criterion for keyword in ['reguliere speeltijd', 'wedstrijd', '1x2', 'match result']):
                outcomes = betoffer.get('outcomes', [])
                for outcome in outcomes:
                    label = outcome.get('label', '').lower()
                    odds = outcome.get('odds')
                    
                    if odds:
                        odds_decimal = odds / 1000  # Kambi stores odds * 1000
                        
                        if label == '1' or home_team.lower() in label:
                            match['odds_1'] = odds_decimal
                        elif label == 'x' or 'gelijkspel' in label or 'draw' in label:
                            match['odds_x'] = odds_decimal
                        elif label == '2' or away_team.lower() in label:
                            match['odds_2'] = odds_decimal
            
            # Over/Under 2.5
            elif 'aantal doelpunten' in criterion or 'over/under' in criterion:
                if '2.5' in criterion or '2,5' in criterion:
                    outcomes = betoffer.get('outcomes', [])
                    for outcome in outcomes:
                        label = outcome.get('label', '').lower()
                        odds = outcome.get('odds')
                        
                        if odds:
                            odds_decimal = odds / 1000
                            
                            if 'over' in label or 'meer' in label:
                                match['over_2_5'] = odds_decimal
                            elif 'under' in label or 'minder' in label:
                                match['under_2_5'] = odds_decimal
            
            # Both Teams To Score
            elif 'beide teams scoren' in criterion or 'both teams to score' in criterion or 'btts' in criterion:
                outcomes = betoffer.get('outcomes', [])
                for outcome in outcomes:
                    label = outcome.get('label', '').lower()
                    odds = outcome.get('odds')
                    
                    if odds:
                        odds_decimal = odds / 1000
                        
                        if 'ja' in label or 'yes' in label:
                            match['btts_yes'] = odds_decimal
                        elif 'nee' in label or 'no' in label:
                            match['btts_no'] = odds_decimal
        
        # Only return if we have main odds
        if match['odds_1'] and match['odds_2']:
            return match
        
        return None
    
    def save_matches(self, matches):
        """Save matches voor AI training"""
        if not matches:
            logger.warning("⚠️ No matches to save!")
            return None, None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # DataFrame
        df = pd.DataFrame(matches)
        
        # Add AI features
        df['implied_prob_home'] = 1 / df['odds_1']
        df['implied_prob_draw'] = 1 / df['odds_x'].fillna(999)
        df['implied_prob_away'] = 1 / df['odds_2']
        df['total_prob'] = df['implied_prob_home'] + df['implied_prob_draw'] + df['implied_prob_away']
        df['margin'] = (df['total_prob'] - 1) * 100
        df['odds_ratio'] = df['odds_1'] / df['odds_2']
        
        # Save CSV
        csv_file = f'data/jacks_matches_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        logger.info(f"💾 CSV saved: {csv_file}")
        
        # Save JSON
        json_file = f'data/jacks_matches_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'scrape_time': timestamp,
                    'total_matches': len(matches),
                    'source': 'jacks.nl (Kambi API)',
                    'method': 'api_direct'
                },
                'matches': matches
            }, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 JSON saved: {json_file}")
        
        # Print summary
        logger.info("="*80)
        logger.info(f"🎉 SUCCESSFULLY SCRAPED {len(matches)} MATCHES!")
        logger.info(f"📊 Leagues: {df['league'].nunique()}")
        logger.info(f"📊 Average odds: 1={df['odds_1'].mean():.2f} X={df['odds_x'].mean():.2f} 2={df['odds_2'].mean():.2f}")
        logger.info(f"💰 Average margin: {df['margin'].mean():.2f}%")
        
        # Top leagues
        top_leagues = df['league'].value_counts().head(5)
        logger.info(f"\n📋 Top 5 Leagues:")
        for league, count in top_leagues.items():
            logger.info(f"   {league}: {count} matches")
        
        logger.info("="*80)
        
        return csv_file, json_file
    
    def run(self):
        """Main execution"""
        logger.info("="*80)
        logger.info("🔥 JACKS.NL COMPLETE SCRAPER")
        logger.info("="*80)
        
        # Fetch matches
        matches = self.fetch_all_football_matches()
        
        if matches:
            # Save
            files = self.save_matches(matches)
            logger.info("✅ Data ready for AI training!")
            return matches
        else:
            logger.warning("⚠️ No matches found")
            return None


if __name__ == '__main__':
    print("="*80)
    print("🔥 JACKS.NL COMPLETE SCRAPER")
    print("Direct API - Fast & Reliable!")
    print("="*80)
    
    try:
        scraper = JacksCompleteScraper()
        matches = scraper.run()
        
        if matches:
            print(f"\n✅ SUCCESS! Scraped {len(matches)} matches!")
            print("🎯 Data ready to feed to AI!")
            
            # Show samples
            print("\n📋 Sample matches:")
            for i, match in enumerate(matches[:5]):
                print(f"\n{i+1}. {match['home_team']} vs {match['away_team']}")
                print(f"   League: {match['league']}")
                print(f"   Odds: {match['odds_1']:.2f} - {match['odds_x']:.2f} - {match['odds_2']:.2f}")
                if match['over_2_5']:
                    print(f"   O/U 2.5: {match['over_2_5']:.2f} / {match['under_2_5']:.2f}")
        else:
            print("\n⚠️ No matches found")
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
