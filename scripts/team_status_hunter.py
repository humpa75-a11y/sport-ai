"""
🏥 ULTIMATE TEAM STATUS HUNTER
==============================

Track EVERYTHING that impacts match outcomes:
1. Injuries (geblesseerde spelers)
2. Suspensions (geschorste spelers)
3. Red cards (rode kaarten)
4. Yellow cards (gele kaarten - suspension risk)
5. Key player availability
6. Team form impact

VREET ALLES WAT DE WEDSTRIJD BEÏNVLOEDT! 🦈
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime, timedelta
import time
import os
import re

class UltimateTeamStatusHunter:
    """Hunt comprehensive team status data"""
    
    def __init__(self):
        self.collected_data = {
            'injuries': [],
            'suspensions': [],
            'yellow_cards': [],
            'red_cards': [],
            'lineup_changes': [],
            'team_news': [],
            'sources': []
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # API keys
        self.api_football_key = os.getenv('API_FOOTBALL_KEY', '6bb5247fdf0b0081a72fc46c853dd210')
    
    def fetch_team_injuries_api(self, team_id):
        """
        Fetch injuries from API-Football
        API endpoint: /injuries
        """
        print("\n" + "="*80)
        print(f"🏥 FETCHING INJURIES (Team ID: {team_id})")
        print("="*80)
        
        url = "https://v3.football.api-sports.io/injuries"
        headers = {'x-apisports-key': self.api_football_key}
        params = {
            'team': team_id,
            'season': 2024
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Save raw response
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = f'data/injuries_team{team_id}_{timestamp}.json'
                os.makedirs('data', exist_ok=True)
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                print(f"[SAVE] Raw data: {save_path}")
                
                injuries = []
                if 'response' in data:
                    for item in data['response']:
                        try:
                            injury = {
                                'team': item['team']['name'],
                                'team_id': item['team']['id'],
                                'player': item['player']['name'],
                                'player_id': item['player']['id'],
                                'injury_type': item['player']['type'],
                                'reason': item['player']['reason'],
                                'start_date': item['fixture']['date'] if 'fixture' in item else None,
                                'expected_return': None,  # Calculate if possible
                                'severity': self._assess_injury_severity(item['player']['type']),
                                'source': 'api-football',
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            injuries.append(injury)
                            print(f"[INJURY] {injury['player']}: {injury['injury_type']} ({injury['severity']})")
                        
                        except KeyError as e:
                            continue
                    
                    self.collected_data['injuries'].extend(injuries)
                    self.collected_data['sources'].append({
                        'type': 'injuries',
                        'source': 'api-football',
                        'team_id': team_id,
                        'count': len(injuries),
                        'file': save_path,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                    print(f"\n[SUCCESS] Found {len(injuries)} injuries")
                    return injuries
            
            else:
                print(f"[ERROR] API returned {response.status_code}")
                print(f"[INFO] Response: {response.text[:300]}")
        
        except Exception as e:
            print(f"[ERROR] Failed to fetch injuries: {e}")
        
        return []
    
    def _assess_injury_severity(self, injury_type):
        """Assess impact on match availability"""
        injury_lower = injury_type.lower()
        
        if any(x in injury_lower for x in ['fracture', 'broken', 'rupture', 'surgery']):
            return 'CRITICAL'  # Out for months
        elif any(x in injury_lower for x in ['strain', 'tear', 'sprain']):
            return 'MAJOR'  # Out for weeks
        elif any(x in injury_lower for x in ['knock', 'bruise', 'fatigue']):
            return 'MINOR'  # Doubtful, may play
        else:
            return 'UNKNOWN'
    
    def fetch_team_cards_api(self, team_id, league_id):
        """
        Fetch yellow/red cards from API-Football
        Track suspension risk
        """
        print("\n" + "="*80)
        print(f"🟨🟥 FETCHING CARDS (Team ID: {team_id})")
        print("="*80)
        
        # Get recent fixtures to analyze cards
        url = "https://v3.football.api-sports.io/fixtures"
        headers = {'x-apisports-key': self.api_football_key}
        params = {
            'team': team_id,
            'league': league_id,
            'season': 2024,
            'last': 20  # Last 20 matches
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = f'data/cards_team{team_id}_{timestamp}.json'
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                
                yellow_cards = []
                red_cards = []
                
                if 'response' in data:
                    for fixture in data['response']:
                        try:
                            # Check if fixture has statistics
                            if 'statistics' not in fixture:
                                continue
                            
                            # Analyze cards for our team
                            for stat in fixture['statistics']:
                                if stat['team']['id'] == team_id:
                                    stats = stat['statistics']
                                    
                                    # Extract card counts
                                    for item in stats:
                                        if item['type'] == 'Yellow Cards':
                                            yellow_count = int(item['value']) if item['value'] else 0
                                            if yellow_count > 0:
                                                yellow_cards.append({
                                                    'team': stat['team']['name'],
                                                    'team_id': team_id,
                                                    'match_date': fixture['fixture']['date'][:10],
                                                    'opponent': fixture['teams']['away']['name'] if fixture['teams']['home']['id'] == team_id else fixture['teams']['home']['name'],
                                                    'yellow_cards': yellow_count,
                                                    'source': 'api-football',
                                                    'scraped_at': datetime.now().isoformat()
                                                })
                                        
                                        elif item['type'] == 'Red Cards':
                                            red_count = int(item['value']) if item['value'] else 0
                                            if red_count > 0:
                                                red_cards.append({
                                                    'team': stat['team']['name'],
                                                    'team_id': team_id,
                                                    'match_date': fixture['fixture']['date'][:10],
                                                    'opponent': fixture['teams']['away']['name'] if fixture['teams']['home']['id'] == team_id else fixture['teams']['home']['name'],
                                                    'red_cards': red_count,
                                                    'suspension_impact': 'SUSPENDED_NEXT_MATCH',
                                                    'source': 'api-football',
                                                    'scraped_at': datetime.now().isoformat()
                                                })
                        
                        except (KeyError, ValueError) as e:
                            continue
                    
                    self.collected_data['yellow_cards'].extend(yellow_cards)
                    self.collected_data['red_cards'].extend(red_cards)
                    
                    print(f"[CARDS] Yellow cards tracked: {len(yellow_cards)} matches")
                    print(f"[CARDS] Red cards tracked: {len(red_cards)} incidents")
                    
                    # Calculate suspension risk
                    total_yellows = sum(c['yellow_cards'] for c in yellow_cards)
                    if total_yellows >= 4:
                        print(f"⚠️  WARNING: {total_yellows} yellow cards - SUSPENSION RISK!")
                    
                    self.collected_data['sources'].append({
                        'type': 'cards',
                        'source': 'api-football',
                        'team_id': team_id,
                        'yellow_matches': len(yellow_cards),
                        'red_incidents': len(red_cards),
                        'file': save_path,
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                    return {'yellows': yellow_cards, 'reds': red_cards}
            
            else:
                print(f"[ERROR] API returned {response.status_code}")
        
        except Exception as e:
            print(f"[ERROR] Failed to fetch cards: {e}")
        
        return {'yellows': [], 'reds': []}
    
    def calculate_team_availability(self, team_id, team_name):
        """
        Calculate team strength based on availability
        Returns: availability_score (0-100%)
        """
        print("\n" + "="*80)
        print(f"📊 CALCULATING TEAM AVAILABILITY: {team_name}")
        print("="*80)
        
        # Filter data for this team
        team_injuries = [i for i in self.collected_data['injuries'] if i.get('team_id') == team_id]
        team_reds = [r for r in self.collected_data['red_cards'] if r.get('team_id') == team_id]
        team_yellows = [y for y in self.collected_data['yellow_cards'] if y.get('team_id') == team_id]
        
        # Impact scores
        injury_impact = 0
        suspension_impact = 0
        yellow_risk = 0
        
        # Injuries impact
        for injury in team_injuries:
            severity = injury.get('severity', 'UNKNOWN')
            if severity == 'CRITICAL':
                injury_impact += 10  # Key player out
            elif severity == 'MAJOR':
                injury_impact += 5
            elif severity == 'MINOR':
                injury_impact += 2
        
        # Red cards = immediate suspension
        suspension_impact = len(team_reds) * 10
        
        # Yellow cards = risk of suspension
        total_yellows = sum(y.get('yellow_cards', 0) for y in team_yellows)
        if total_yellows >= 4:
            yellow_risk = 5  # High risk
        elif total_yellows >= 3:
            yellow_risk = 3  # Moderate risk
        
        # Calculate availability (100% = full strength)
        total_impact = injury_impact + suspension_impact + yellow_risk
        availability_score = max(0, 100 - total_impact)
        
        availability = {
            'team': team_name,
            'team_id': team_id,
            'availability_score': availability_score,
            'injuries_count': len(team_injuries),
            'injuries_impact': injury_impact,
            'suspensions_count': len(team_reds),
            'suspension_impact': suspension_impact,
            'yellow_cards_total': total_yellows,
            'yellow_risk': yellow_risk,
            'total_impact': total_impact,
            'calculated_at': datetime.now().isoformat()
        }
        
        print(f"\n[AVAILABILITY] Score: {availability_score}% (100% = full strength)")
        print(f"  Injuries: {len(team_injuries)} ({injury_impact} impact)")
        print(f"  Suspensions: {len(team_reds)} ({suspension_impact} impact)")
        print(f"  Yellow cards: {total_yellows} ({yellow_risk} risk)")
        
        if availability_score < 80:
            print(f"  ⚠️  WARNING: Team significantly weakened!")
        
        return availability
    
    def scrape_transfermarkt_injuries(self, team_name):
        """
        Scrape Transfermarkt for detailed injury info
        Source: transfermarkt.com (has comprehensive injury database)
        """
        print("\n" + "="*80)
        print(f"🏥 SCRAPING TRANSFERMARKT: {team_name}")
        print("="*80)
        
        # Transfermarkt URLs (example)
        # Note: Requires proper team slug/ID
        team_slug = team_name.lower().replace(' ', '-')
        url = f"https://www.transfermarkt.com/{team_slug}/injuries/verein/XXX"  # Need team ID
        
        print(f"[INFO] Transfermarkt scraping requires team IDs")
        print(f"[INFO] Alternative: Use API-Football for comprehensive data")
        
        # Placeholder for implementation
        return []
    
    def generate_match_impact_report(self, home_team_id, away_team_id, home_team_name, away_team_name):
        """
        Generate comprehensive match impact report
        Shows how injuries/suspensions affect the match
        """
        print("\n" + "="*80)
        print(f"📋 MATCH IMPACT REPORT")
        print("="*80)
        print(f"{home_team_name} vs {away_team_name}")
        print("="*80)
        
        # Get availability for both teams
        home_avail = self.calculate_team_availability(home_team_id, home_team_name)
        away_avail = self.calculate_team_availability(away_team_id, away_team_name)
        
        # Compare
        availability_diff = home_avail['availability_score'] - away_avail['availability_score']
        
        print(f"\n📊 TEAM COMPARISON:")
        print(f"  {home_team_name}: {home_avail['availability_score']}%")
        print(f"  {away_team_name}: {away_avail['availability_score']}%")
        print(f"  Difference: {abs(availability_diff):.1f}%")
        
        if abs(availability_diff) > 15:
            advantage = home_team_name if availability_diff > 0 else away_team_name
            print(f"\n  🎯 SIGNIFICANT ADVANTAGE: {advantage}")
        
        report = {
            'home_team': home_team_name,
            'away_team': away_team_name,
            'home_availability': home_avail,
            'away_availability': away_avail,
            'availability_difference': availability_diff,
            'match_impact': 'HIGH' if abs(availability_diff) > 15 else ('MEDIUM' if abs(availability_diff) > 8 else 'LOW'),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def save_all_data(self):
        """Save all collected team status data"""
        print("\n" + "="*80)
        print("💾 SAVING TEAM STATUS DATA")
        print("="*80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save injuries
        if self.collected_data['injuries']:
            df = pd.DataFrame(self.collected_data['injuries'])
            csv_file = f'data/team_injuries_{timestamp}.csv'
            df.to_csv(csv_file, index=False)
            print(f"[SAVE] Injuries: {csv_file} ({len(df)} rows)")
        
        # Save red cards
        if self.collected_data['red_cards']:
            df = pd.DataFrame(self.collected_data['red_cards'])
            csv_file = f'data/team_red_cards_{timestamp}.csv'
            df.to_csv(csv_file, index=False)
            print(f"[SAVE] Red cards: {csv_file} ({len(df)} rows)")
        
        # Save yellow cards
        if self.collected_data['yellow_cards']:
            df = pd.DataFrame(self.collected_data['yellow_cards'])
            csv_file = f'data/team_yellow_cards_{timestamp}.csv'
            df.to_csv(csv_file, index=False)
            print(f"[SAVE] Yellow cards: {csv_file} ({len(df)} rows)")
        
        # Save complete data with sources
        json_file = f'data/team_status_complete_{timestamp}.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.collected_data, f, indent=2, ensure_ascii=False)
        print(f"[SAVE] Complete data: {json_file}")
        
        print("\n" + "="*80)
        print("📊 COLLECTION SUMMARY")
        print("="*80)
        print(f"Injuries: {len(self.collected_data['injuries'])}")
        print(f"Red cards: {len(self.collected_data['red_cards'])}")
        print(f"Yellow cards: {len(self.collected_data['yellow_cards'])}")
        print(f"Sources: {len(self.collected_data['sources'])}")
        print("="*80)


def test_team_status_hunter():
    """Test with example teams"""
    print("\n" + "="*80)
    print("🦈 ULTIMATE TEAM STATUS HUNTER - TEST RUN")
    print("="*80)
    print(f"Time: {datetime.now()}")
    print("="*80 + "\n")
    
    hunter = UltimateTeamStatusHunter()
    
    # Example teams (API-Football IDs)
    teams = [
        (33, 'Manchester United', 39),  # (team_id, name, league_id)
        (40, 'Liverpool', 39),
        (50, 'Manchester City', 39),
        (42, 'Arsenal', 39),
    ]
    
    print("🎯 Hunting data for Premier League teams...\n")
    
    for team_id, team_name, league_id in teams:
        print(f"\n{'='*80}")
        print(f"📊 TEAM: {team_name}")
        print(f"{'='*80}")
        
        # Fetch injuries
        hunter.fetch_team_injuries_api(team_id)
        time.sleep(2)  # Rate limiting
        
        # Fetch cards
        hunter.fetch_team_cards_api(team_id, league_id)
        time.sleep(2)
    
    # Generate example match report
    print("\n" + "="*80)
    print("🎯 EXAMPLE MATCH IMPACT REPORT")
    print("="*80)
    
    report = hunter.generate_match_impact_report(
        home_team_id=50,
        away_team_id=42,
        home_team_name='Manchester City',
        away_team_name='Arsenal'
    )
    
    # Save everything
    hunter.save_all_data()
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETE!")
    print("="*80)
    print(f"Check data/ folder for results")
    print("="*80 + "\n")
    
    return hunter


if __name__ == '__main__':
    hunter = test_team_status_hunter()
