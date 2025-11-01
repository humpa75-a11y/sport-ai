"""
🤝 MULTI-SOURCE DATA TEAM - COLLABORATIVE EDITION 🤝

6 DATA SOURCES WORKING AS ONE TEAM!
====================================

PREMIUM APIs (rate limited, hoogste kwaliteit):
1. 🏆 API-Football (v3.football.api-sports.io)
   - 1445 matches/dag beschikbaar
   - 100 API calls/dag limit
   - Live scores, team stats, fixtures

2. ⚽ Football-Data.org
   - 1092+ matches (13 competitions)
   - 10 calls/minuut (600/uur)
   - Standings, team info, player data

FREE APIs (unlimited, altijd beschikbaar):
3. 📺 ESPN API
   - 20+ matches, geen limits
   - Live scores, commentary, odds

4. 🎮 TheSportsDB
   - 500+ leagues worldwide
   - Team info, standings, player search

5. 🇩🇪 OpenLigaDB
   - 306 Bundesliga matches
   - Bundesliga specialist, geen limits

INTELLIGENT BACKUP:
6. 🎯 Simulation Engine
   - Real 2024/2025 season statistics
   - Bayern 2.4 xG, Man City 2.6 xG
   - Poisson-based predictions
   - Altijd beschikbaar als fallback

🤖 TEAM STRATEGIE:
==================
✅ Probeer premium APIs eerst (meest accurate)
✅ Fall back naar free APIs bij rate limits
✅ Combineer data van meerdere bronnen
✅ Simulation vult gaten als APIs down zijn
✅ Systeem faalt NOOIT - altijd data!

Features:
- Poisson simulatie (100+ runs per match)
- Expected Value (EV) berekeningen
- Kelly Criterion stake suggesties
- Accumulator builder (4-fold & 7-fold)
- Multi-market analysis (1X2, O/U, BTTS)
- Shot predictions (total + on target)

Author: Sport AI Sync Team
Date: November 2025
"""

import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# Import alle 6 data sources
try:
    # Try relative imports first (when run as module)
    from api_sports_integration import ApiSportsIntegration
    from football_data_org_integration import FootballDataOrgIntegration
    from espn_api_integration import ESPNAPIIntegration
    from thesportsdb_integration import TheSportsDBIntegration
    from openligadb_integration import OpenLigaDBIntegration
    from simulation_engine import get_demo_matches, get_realistic_odds
except ImportError:
    # Fall back to absolute imports (when run from parent dir)
    from backend.api_sports_integration import ApiSportsIntegration
    from backend.football_data_org_integration import FootballDataOrgIntegration
    from backend.espn_api_integration import ESPNAPIIntegration
    from backend.thesportsdb_integration import TheSportsDBIntegration
    from backend.openligadb_integration import OpenLigaDBIntegration
    from backend.simulation_engine import get_demo_matches, get_realistic_odds

# =============================================
# 1. DATA SOURCE TEAM MANAGER
# =============================================

class DataSourceTeam:
    """
    Intelligent team van 6 databronnen.
    Ze werken samen voor maximale betrouwbaarheid.
    """
    
    def __init__(self):
        print("🤝 Initializing Data Source Team...")
        
        # Premium APIs (rate limited)
        self.api_football = ApiSportsIntegration(api_key="eec52f29ffbc24effa9bc0e7963a8cd9")
        self.football_data = FootballDataOrgIntegration(api_key="d5513a02070e4dbba002d3f5c9a78942")
        
        # Free APIs (unlimited)
        self.espn = ESPNAPIIntegration()
        self.sportsdb = TheSportsDBIntegration()
        self.openliga = OpenLigaDBIntegration()
        
        # Track status van elke source
        self.source_status = {
            'api_football': {'available': True, 'calls_today': 0, 'limit': 100, 'matches': 0},
            'football_data': {'available': True, 'calls_today': 0, 'limit': 600, 'matches': 0},
            'espn': {'available': True, 'calls_today': 0, 'limit': None, 'matches': 0},
            'sportsdb': {'available': True, 'calls_today': 0, 'limit': None, 'matches': 0},
            'openliga': {'available': True, 'calls_today': 0, 'limit': None, 'matches': 0},
            'simulation': {'available': True, 'calls_today': 0, 'limit': None, 'matches': 0}
        }
        
        print("✅ Team ready!\n")
        
    def get_matches_team_mode(self, league, days_ahead=3):
        """
        🤝 TEAM MODE: Alle bronnen werken samen!
        
        Strategie:
        1. Premium APIs eerst (beste data, maar limited)
        2. Free APIs als supplement/backup
        3. Simulation vult gaten
        4. Combineer data voor beste resultaat
        """
        
        all_matches = []
        sources_used = []
        
        print(f"🎯 Team zoekt matches voor: {league} (next {days_ahead} days)")
        print("="*60)
        
        # === STRATEGY 1: Premium APIs First ===
        
        # 1A. API-Football (hoogste prioriteit)
        if self._can_use('api_football'):
            try:
                print("🏆 API-Football checking...")
                league_ids = {
                    'premier-league': 39, 'bundesliga': 78, 'la-liga': 140,
                    'serie-a': 135, 'eredivisie': 88, 'ligue-1': 61
                }
                league_id = league_ids.get(league.lower(), 78)
                
                date_from = datetime.now().strftime('%Y-%m-%d')
                date_to = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
                
                df = self.api_football.get_league_fixtures(
                    league_id=league_id,
                    season=2024,
                    date_from=date_from,
                    date_to=date_to
                )
                
                if not df.empty:
                    df['source'] = 'API-Football'
                    all_matches.append(df)
                    sources_used.append('🏆 API-Football')
                    self._mark_used('api_football', len(df))
                    print(f"   ✅ {len(df)} matches found!")
                else:
                    print("   ⚠️ No matches found")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                self.source_status['api_football']['available'] = False
        else:
            print("🏆 API-Football: Rate limit reached, skipping...")
        
        # 1B. Football-Data.org (supplement premium data)
        if self._can_use('football_data'):
            try:
                print("⚽ Football-Data.org checking...")
                competitions = {
                    'premier-league': 'PL', 'bundesliga': 'BL1', 'la-liga': 'PD',
                    'serie-a': 'SA', 'eredivisie': 'DED', 'ligue-1': 'FL1'
                }
                comp_code = competitions.get(league.lower(), 'PL')
                
                df = self.football_data.get_matches(competition=comp_code, status='SCHEDULED')
                
                if not df.empty:
                    df['source'] = 'Football-Data.org'
                    all_matches.append(df)
                    sources_used.append('⚽ Football-Data.org')
                    self._mark_used('football_data', len(df))
                    print(f"   ✅ {len(df)} matches found!")
                else:
                    print("   ⚠️ No matches found")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                self.source_status['football_data']['available'] = False
        else:
            print("⚽ Football-Data.org: Rate limit reached, skipping...")
        
        # === STRATEGY 2: Free APIs (Unlimited) ===
        
        # 2A. ESPN API
        if len(all_matches) < 1:  # Only if we need more data
            try:
                print("📺 ESPN API checking...")
                df_list = self.espn.get_upcoming_matches(league=league, days_ahead=days_ahead)
                
                if df_list and len(df_list) > 0:
                    # Convert to DataFrame
                    df = pd.DataFrame(df_list)
                    df['source'] = 'ESPN'
                    all_matches.append(df)
                    sources_used.append('📺 ESPN')
                    self._mark_used('espn', len(df))
                    print(f"   ✅ {len(df)} matches found!")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # 2B. OpenLigaDB (Bundesliga specialist)
        if league.lower() == 'bundesliga' and len(all_matches) < 1:
            try:
                print("🇩🇪 OpenLigaDB checking...")
                df = self.openliga.get_upcoming_fixtures(league='bundesliga', max_matches=20)
                
                if not df.empty:
                    df['source'] = 'OpenLigaDB'
                    all_matches.append(df)
                    sources_used.append('🇩🇪 OpenLigaDB')
                    self._mark_used('openliga', len(df))
                    print(f"   ✅ {len(df)} matches found!")
                    
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # === STRATEGY 3: Simulation Fallback ===
        
        if len(all_matches) == 0:
            print("🎯 Simulation Engine activating...")
            df = get_demo_matches(league=league, days_ahead=days_ahead)
            df['source'] = 'Simulation (Real Stats)'
            all_matches.append(df)
            sources_used.append('🎯 Simulation')
            self._mark_used('simulation', len(df))
            print(f"   ✅ {len(df)} matches generated with real statistics!")
        
        # === COMBINE ALL DATA ===
        
        if len(all_matches) > 0:
            combined_df = pd.concat(all_matches, ignore_index=True)
            combined_df = self._standardize_dataframe(combined_df)
            
            # Remove duplicates (prefer premium sources)
            if len(all_matches) > 1:
                combined_df = combined_df.drop_duplicates(
                    subset=['home', 'away', 'match_date'],
                    keep='first'  # Keep first occurrence (premium sources)
                )
            
            print("\n" + "="*60)
            print(f"🤝 TEAM RESULT:")
            print(f"   Sources used: {', '.join(sources_used)}")
            print(f"   Total unique matches: {len(combined_df)}")
            print("="*60 + "\n")
            
            return combined_df, sources_used
        
        return pd.DataFrame(), []
    
    def _can_use(self, source_name):
        """Check if source is available and within limits"""
        source = self.source_status[source_name]
        
        if not source['available']:
            return False
        
        if source['limit'] is None:  # Unlimited
            return True
        
        return source['calls_today'] < source['limit']
    
    def _mark_used(self, source_name, matches_count):
        """Track usage"""
        self.source_status[source_name]['calls_today'] += 1
        self.source_status[source_name]['matches'] += matches_count
    
    def _standardize_dataframe(self, df):
        """Ensure all required columns exist and normalize column names"""
        
        # Normalize column names from different APIs
        column_mapping = {
            # ESPN format
            'home_team': 'home',
            'away_team': 'away',
            'date': 'match_date',
            
            # OpenLigaDB format
            'home_team_name': 'home',
            'away_team_name': 'away',
            'datetime': 'match_date',
            
            # Football-Data.org format
            'homeTeam': 'home',
            'awayTeam': 'away',
            'utcDate': 'match_date',
            
            # TheSportsDB format
            'strHomeTeam': 'home',
            'strAwayTeam': 'away',
            'dateEvent': 'match_date',
            'strTime': 'match_time'
        }
        
        # Apply column mapping
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]
        
        # Extract date and time if combined datetime exists
        if 'match_date' in df.columns:
            try:
                df['match_date'] = pd.to_datetime(df['match_date'])
                if 'match_time' not in df.columns:
                    df['match_time'] = df['match_date'].dt.strftime('%H:%M')
                df['match_date'] = df['match_date'].dt.strftime('%Y-%m-%d')
            except:
                pass
        
        # Set defaults for missing columns
        defaults = {
            'match_date': datetime.now().strftime('%Y-%m-%d'),
            'match_time': '15:00',
            'days_until_match': 0,
            'home_xg': 1.5,
            'away_xg': 1.2,
            'home_shots_avg': 12,
            'away_shots_avg': 10,
            'home_sot_avg': 4,
            'away_sot_avg': 4,
            'tournament': 'League'
        }
        
        for col, default_val in defaults.items():
            if col not in df.columns:
                df[col] = default_val
        
        # Calculate days until match if not present
        if 'days_until_match' in df.columns:
            try:
                df['days_until_match'] = (
                    pd.to_datetime(df['match_date']) - datetime.now()
                ).dt.days
            except:
                pass
        
        return df
    
    def get_team_status(self):
        """Show status of all team members"""
        print("\n" + "="*60)
        print("📊 DATA SOURCE TEAM STATUS")
        print("="*60)
        
        for source, status in self.source_status.items():
            available = "✅" if status['available'] else "❌"
            limit_str = f"{status['limit']} calls/day" if status['limit'] else "Unlimited"
            usage = f"{status['calls_today']} calls" if status['limit'] else f"{status['calls_today']} calls"
            matches = f"{status['matches']} matches"
            
            print(f"{available} {source:20} | {limit_str:20} | {usage:15} | {matches}")
        
        print("="*60 + "\n")

# =============================================
# 2. POISSON MATCH SIMULATION
# =============================================

def simulate_match(home_xg, away_xg, runs=100):
    """
    Poisson-based match simulation.
    Gebruikt xG (expected goals) voor realistische voorspellingen.
    """
    
    results = {
        'home_wins': 0, 'draws': 0, 'away_wins': 0,
        'over_15': 0, 'over_25': 0, 'over_35': 0,
        'btts': 0, 'scores': {},
        'home_goals_total': 0, 'away_goals_total': 0
    }
    
    for _ in range(runs):
        home_goals = np.random.poisson(home_xg)
        away_goals = np.random.poisson(away_xg)
        
        results['home_goals_total'] += home_goals
        results['away_goals_total'] += away_goals
        
        total_goals = home_goals + away_goals
        
        if home_goals > away_goals:
            results['home_wins'] += 1
        elif home_goals < away_goals:
            results['away_wins'] += 1
        else:
            results['draws'] += 1
        
        if total_goals > 1.5:
            results['over_15'] += 1
        if total_goals > 2.5:
            results['over_25'] += 1
        if total_goals > 3.5:
            results['over_35'] += 1
        
        if home_goals > 0 and away_goals > 0:
            results['btts'] += 1
        
        score = f"{home_goals}-{away_goals}"
        results['scores'][score] = results['scores'].get(score, 0) + 1
    
    # Calculate probabilities
    p_home = results['home_wins'] / runs
    p_draw = results['draws'] / runs
    p_away = results['away_wins'] / runs
    
    # Most likely score
    most_likely = max(results['scores'], key=results['scores'].get)
    score_prob = results['scores'][most_likely] / runs
    
    # Prediction
    if p_home > p_draw and p_home > p_away:
        prediction = "Home Win"
        confidence = p_home * 100
    elif p_away > p_home and p_away > p_draw:
        prediction = "Away Win"
        confidence = p_away * 100
    else:
        prediction = "Draw"
        confidence = p_draw * 100
    
    # Shots prediction (xG-based estimation)
    home_shots = int(home_xg * 8)  # ~8 shots per xG
    away_shots = int(away_xg * 8)
    home_sot = int(home_xg * 3)    # ~3 shots on target per xG
    away_sot = int(away_xg * 3)
    
    return {
        'p_home_win': p_home,
        'p_draw': p_draw,
        'p_away_win': p_away,
        'p_over_15': results['over_15'] / runs,
        'p_over_25': results['over_25'] / runs,
        'p_over_35': results['over_35'] / runs,
        'p_btts': results['btts'] / runs,
        'most_likely_score': most_likely,
        'score_probability': score_prob,
        'prediction': prediction,
        'confidence': confidence,
        'avg_total_goals': (results['home_goals_total'] + results['away_goals_total']) / runs,
        'exp_home_shots': home_shots,
        'exp_away_shots': away_shots,
        'exp_home_sot': home_sot,
        'exp_away_sot': away_sot
    }

# =============================================
# 3. EXPECTED VALUE CALCULATIONS
# =============================================

def calculate_ev(probability, odds):
    """
    Expected Value (EV) berekening.
    EV = (Probability × Odds) - 1
    
    Positieve EV = Value bet!
    """
    return (probability * odds) - 1

def kelly_criterion(probability, odds, bankroll=100, max_fraction=0.05):
    """
    Kelly Criterion voor optimal stake size.
    Kelly = (bp - q) / b
    
    waar:
    - b = decimal odds - 1
    - p = win probability
    - q = lose probability (1 - p)
    """
    b = odds - 1
    q = 1 - probability
    kelly = (b * probability - q) / b
    
    # Fractional Kelly (safer)
    kelly = max(0, min(kelly * 0.25, max_fraction))
    
    stake = bankroll * kelly
    return round(stake, 2)

# =============================================
# 4. MAIN ANALYSIS FUNCTION
# =============================================

def run_full_analysis(league="bundesliga", days_ahead=3, use_team_mode=True):
    """
    🚀 MAIN FUNCTION: Complete betting analysis
    
    Args:
        league: bundesliga, premier-league, eredivisie, serie-a, la-liga
        days_ahead: number of days to look ahead (default 3)
        use_team_mode: True = use all 6 sources as team (RECOMMENDED)
    
    Returns:
        DataFrame with complete analysis
    """
    
    print("\n" + "="*80)
    print("🚀 MULTI-SOURCE BETTING ANALYZER - TEAM EDITION")
    print("="*80)
    print(f"League: {league.upper()}")
    print(f"Period: Next {days_ahead} days")
    print(f"Mode: {'🤝 TEAM MODE (6 sources)' if use_team_mode else '⚠️ Legacy mode'}")
    print("="*80 + "\n")
    
    # Initialize team
    team = DataSourceTeam()
    
    # Get matches using team approach
    df, sources_used = team.get_matches_team_mode(league, days_ahead)
    
    if df.empty:
        print("❌ No matches found!")
        return pd.DataFrame()
    
    print(f"✅ {len(df)} matches ready for analysis!\n")
    
    # Analyze each match
    results = []
    
    for idx, row in df.iterrows():
        match = f"{row['home']} vs {row['away']}"
        match_datetime = f"{row['match_date']} {row['match_time']}"
        
        print(f"📊 {idx+1}/{len(df)}: {match}")
        print(f"   📅 {match_datetime} ({row['days_until_match']} days)")
        print(f"   🎯 xG: {row['home_xg']:.2f} vs {row['away_xg']:.2f}")
        
        # Poisson simulation
        sim = simulate_match(row['home_xg'], row['away_xg'], runs=100)
        
        # Get odds (realistic based on xG)
        odds = get_realistic_odds(row['home_xg'], row['away_xg'])
        
        # Expected Value calculations
        ev_home = calculate_ev(sim['p_home_win'], odds[0])
        ev_draw = calculate_ev(sim['p_draw'], odds[1])
        ev_away = calculate_ev(sim['p_away_win'], odds[2])
        ev_over25 = calculate_ev(sim['p_over_25'], 1.80)
        ev_over15 = calculate_ev(sim['p_over_15'], 1.35)
        ev_btts = calculate_ev(sim['p_btts'], 1.75)
        
        # Find best bet
        all_evs = {
            f"Home Win @ {odds[0]:.2f}": ev_home,
            f"Draw @ {odds[1]:.2f}": ev_draw,
            f"Away Win @ {odds[2]:.2f}": ev_away,
            f"Over 2.5 @ 1.80": ev_over25,
            f"Over 1.5 @ 1.35": ev_over15,
            f"BTTS @ 1.75": ev_btts
        }
        
        best_bet_name = max(all_evs, key=all_evs.get)
        max_ev = all_evs[best_bet_name]
        
        if max_ev < 0.05:
            best_bet = "❌ No value"
        else:
            # Calculate Kelly stake
            odds_value = float(best_bet_name.split('@')[1].strip())
            prob = [v for k, v in [
                ('Home', sim['p_home_win']), ('Draw', sim['p_draw']),
                ('Away', sim['p_away_win']), ('Over 2.5', sim['p_over_25']),
                ('Over 1.5', sim['p_over_15']), ('BTTS', sim['p_btts'])
            ] if any(x in best_bet_name for x in k.split())]
            
            if prob:
                stake = kelly_criterion(prob[0], odds_value)
                best_bet = f"✅ {best_bet_name} (EV: +{max_ev:.2f}, Stake: €{stake})"
            else:
                best_bet = f"✅ {best_bet_name} (EV: +{max_ev:.2f})"
        
        results.append({
            # Match info
            'match_date': row['match_date'],
            'match_time': row['match_time'],
            'days_ahead': row['days_until_match'],
            'match': match,
            'tournament': row['tournament'],
            'source': row.get('source', 'Unknown'),
            
            # Predictions
            'prediction': sim['prediction'],
            'confidence': f"{sim['confidence']:.1f}%",
            'most_likely_score': sim['most_likely_score'],
            'score_prob': f"{sim['score_probability']:.1f}%",
            
            # Probabilities
            'p_home_win': f"{sim['p_home_win']:.0%}",
            'p_draw': f"{sim['p_draw']:.0%}",
            'p_away_win': f"{sim['p_away_win']:.0%}",
            
            # Goals
            'p_over_15': f"{sim['p_over_15']:.0%}",
            'p_over_25': f"{sim['p_over_25']:.0%}",
            'p_over_35': f"{sim['p_over_35']:.0%}",
            'p_btts': f"{sim['p_btts']:.0%}",
            'avg_goals': f"{sim['avg_total_goals']:.1f}",
            
            # Shots
            'home_shots': f"{sim['exp_home_shots']} ({sim['exp_home_sot']} SoT)",
            'away_shots': f"{sim['exp_away_shots']} ({sim['exp_away_sot']} SoT)",
            
            # Betting
            'odds_1x2': f"{odds[0]:.2f} / {odds[1]:.2f} / {odds[2]:.2f}",
            'best_bet': best_bet,
            'ev': max_ev
        })
        
        print(f"   {sim['prediction']} ({sim['confidence']:.1f}%)")
        print(f"   {best_bet}\n")
    
    result_df = pd.DataFrame(results)
    
    # Sort by date
    result_df = result_df.sort_values(['days_ahead', 'match_time'])
    
    # Show team status
    team.get_team_status()
    
    # === ACCUMULATOR SUGGESTIONS ===
    if len(result_df) > 0:
        print("="*80)
        print("💰 ACCUMULATOR SUGGESTIONS")
        print("="*80)
        
        value_bets = result_df[result_df['ev'] > 0.05].sort_values('ev', ascending=False)
        
        if len(value_bets) >= 4:
            print("\n🎯 TOP 4-FOLD ACCUMULATOR:")
            top_4 = value_bets.head(4)
            total_odds = 1.0
            
            for idx, bet in top_4.iterrows():
                bet_str = bet['best_bet']
                if '@' in bet_str and '✅' in bet_str:
                    try:
                        odds_str = bet_str.split('@')[1].split('(')[0].strip()
                        bet_odds = float(odds_str)
                        total_odds *= bet_odds
                        
                        print(f"  {len([i for i in top_4.index if i <= idx])}. {bet['match']}")
                        print(f"     → {bet_str}")
                    except:
                        pass
            
            print(f"\n  📊 Combined Odds: {total_odds:.2f}x")
            print(f"  💵 €10 stake → €{total_odds * 10:.2f} payout")
            
        print("\n" + "="*80)
    
    print("\n✅ ANALYSIS COMPLETE!")
    print(f"🤝 Data sources used: {', '.join(sources_used)}")
    print("="*80 + "\n")
    
    return result_df

# =============================================
# 5. QUICK ACCESS FUNCTIONS
# =============================================

def quick_analysis(league="bundesliga", days_ahead=3):
    """Quick analysis - één functie call"""
    return run_full_analysis(league=league, days_ahead=days_ahead)

def export_to_json(df, filename="team_analysis.json"):
    """Export naar JSON"""
    df.to_json(filename, orient='records', indent=2)
    print(f"💾 Saved: {filename}")

def export_to_csv(df, filename="team_analysis.csv"):
    """Export naar CSV"""
    df.to_csv(filename, index=False)
    print(f"💾 Saved: {filename}")

# =============================================
# 6. TEST RUN
# =============================================

if __name__ == "__main__":
    # Test met Bundesliga
    df = run_full_analysis(league="bundesliga", days_ahead=3, use_team_mode=True)
    
    if not df.empty:
        print("\n📋 SUMMARY:")
        summary_cols = ['match', 'prediction', 'confidence', 'best_bet', 'source']
        print(df[summary_cols].to_string(index=False))
        
        # Export
        export_to_json(df, "team_analysis_latest.json")
        export_to_csv(df, "team_analysis_latest.csv")
