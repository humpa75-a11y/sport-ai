"""
🏆 TEAM DATABASE BUILDER - De Meester's Geheugen 🏆

Dit script bouwt een intelligente database van alle teams met:
- Historische statistieken
- Huidige vorm
- Aanvals/verdedigingskracht
- Fuzzy matching voor team namen
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from difflib import SequenceMatcher

def similar(a, b):
    """Berekent similarity tussen twee strings voor fuzzy matching."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def load_all_historical_data():
    """Laad alle historische data uit de data folder."""
    print("📚 Laden van alle historische data...")
    
    # Zoek naar alle CSV bestanden in data folder
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    all_data = []
    
    # Laad ook de daily learning log als die bestaat
    daily_log = os.path.join(data_dir, 'daily_learning_log.csv')
    if os.path.exists(daily_log):
        try:
            df = pd.read_csv(daily_log)
            df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
            all_data.append(df)
            print(f"   ✅ Daily learning log geladen: {len(df)} wedstrijden")
        except Exception as e:
            print(f"   ⚠️ Kon daily log niet laden: {e}")
    
    # Als we geen data hebben, download de meest recente data
    if not all_data:
        print("   ⚠️ Geen lokale data gevonden. Data wordt nu gedownload...")
        import sys
        import requests
        import io
        
        # Download data voor huidige seizoen
        current_year = datetime.now().year
        season_str = str(current_year)[-2:] + str(current_year + 1)[-2:]
        
        leagues = {
            "Premier League": "E0",
            "La Liga": "SP1",
            "Bundesliga": "D1",
            "Serie A": "I1",
            "Ligue 1": "F1"
        }
        
        for league_name, league_code in leagues.items():
            url = f"https://www.football-data.co.uk/mmz4281/{season_str}/{league_code}.csv"
            try:
                response = requests.get(url)
                response.raise_for_status()
                df = pd.read_csv(io.StringIO(response.content.decode('latin-1')))
                df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
                all_data.append(df)
                print(f"   ✅ {league_name} geladen: {len(df)} wedstrijden")
            except Exception as e:
                print(f"   ⚠️ Kon {league_name} niet downloaden: {e}")
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"✅ Totaal {len(combined_df)} wedstrijden geladen")
        return combined_df
    else:
        print("❌ Kon geen data laden")
        return None

def calculate_team_stats(df, team_name, is_home=True):
    """Bereken uitgebreide statistieken voor een team."""
    
    if is_home:
        team_matches = df[df['HomeTeam'] == team_name].copy()
        goals_for = 'FTHG'
        goals_against = 'FTAG'
        result_col = 'FTR'
        win_val = 'H'
        loss_val = 'A'
    else:
        team_matches = df[df['AwayTeam'] == team_name].copy()
        goals_for = 'FTAG'
        goals_against = 'FTHG'
        result_col = 'FTR'
        win_val = 'A'
        loss_val = 'H'
    
    if len(team_matches) == 0:
        return None
    
    # Sorteer op datum (meest recent eerst)
    team_matches = team_matches.sort_values('Date', ascending=False)
    
    # Basis statistieken
    total_games = len(team_matches)
    wins = len(team_matches[team_matches[result_col] == win_val])
    draws = len(team_matches[team_matches[result_col] == 'D'])
    losses = len(team_matches[team_matches[result_col] == loss_val])
    
    # Goal statistieken
    goals_scored = team_matches[goals_for].sum()
    goals_conceded = team_matches[goals_against].sum()
    
    # Laatste 5 wedstrijden (vorm)
    last_5 = team_matches.head(5)
    last_5_wins = len(last_5[last_5[result_col] == win_val])
    last_5_goals_scored = last_5[goals_for].sum()
    last_5_goals_conceded = last_5[goals_against].sum()
    
    # Bereken form score (gewogen: recent = belangrijker)
    form_points = []
    for idx, match in last_5.iterrows():
        if match[result_col] == win_val:
            form_points.append(3)
        elif match[result_col] == 'D':
            form_points.append(1)
        else:
            form_points.append(0)
    
    # Gewogen gemiddelde (meest recente = zwaarder)
    weights = [0.4, 0.3, 0.15, 0.1, 0.05]  # Meest recent eerst
    form_score = sum(p * w for p, w in zip(form_points, weights[:len(form_points)])) if form_points else 0
    
    stats = {
        'team_name': team_name,
        'total_games': int(total_games),
        'wins': int(wins),
        'draws': int(draws),
        'losses': int(losses),
        'win_rate': wins / total_games if total_games > 0 else 0,
        'goals_scored': int(goals_scored),
        'goals_conceded': int(goals_conceded),
        'avg_goals_scored': goals_scored / total_games if total_games > 0 else 0,
        'avg_goals_conceded': goals_conceded / total_games if total_games > 0 else 0,
        'goal_difference': int(goals_scored - goals_conceded),
        'last_5_wins': int(last_5_wins),
        'last_5_goals_scored': int(last_5_goals_scored),
        'last_5_goals_conceded': int(last_5_goals_conceded),
        'form_score': round(form_score, 2),
        'attack_strength': round((goals_scored / total_games) * (1 + wins / total_games), 2) if total_games > 0 else 0,
        'defense_strength': round(3.0 - (goals_conceded / total_games), 2) if total_games > 0 else 0,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return stats

def build_team_database():
    """Bouw de complete team database."""
    print("\n" + "="*80)
    print("🏆 TEAM DATABASE BUILDER: GESTART")
    print("="*80 + "\n")
    
    # Laad data
    df = load_all_historical_data()
    
    if df is None or len(df) == 0:
        print("❌ Geen data beschikbaar om database te bouwen")
        return
    
    # Extraheer alle unieke teams
    home_teams = set(df['HomeTeam'].dropna().unique())
    away_teams = set(df['AwayTeam'].dropna().unique())
    all_teams = sorted(home_teams.union(away_teams))
    
    print(f"🔍 {len(all_teams)} unieke teams gevonden\n")
    
    # Bouw database
    team_database = {}
    
    for team in all_teams:
        print(f"   📊 Verwerken: {team}...", end=" ")
        
        # Bereken home en away statistieken
        home_stats = calculate_team_stats(df, team, is_home=True)
        away_stats = calculate_team_stats(df, team, is_home=False)
        
        # Combineer overall statistieken
        if home_stats and away_stats:
            overall_stats = {
                'team_name': team,
                'total_games': home_stats['total_games'] + away_stats['total_games'],
                'overall_win_rate': (home_stats['wins'] + away_stats['wins']) / (home_stats['total_games'] + away_stats['total_games']),
                'overall_avg_goals_scored': (home_stats['goals_scored'] + away_stats['goals_scored']) / (home_stats['total_games'] + away_stats['total_games']),
                'overall_avg_goals_conceded': (home_stats['goals_conceded'] + away_stats['goals_conceded']) / (home_stats['total_games'] + away_stats['total_games']),
                'home_stats': home_stats,
                'away_stats': away_stats,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            team_database[team] = overall_stats
            print("✅")
        else:
            print("⚠️ Niet genoeg data")
    
    # Sla database op
    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_database.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(team_database, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Team database opgeslagen: {output_path}")
    print(f"📊 {len(team_database)} teams in database")
    
    # Maak ook een naam-mapping voor fuzzy matching
    build_team_name_mapping(all_teams)
    
    print("\n" + "="*80)
    print("🏆 TEAM DATABASE BUILDER: VOLTOOID")
    print("="*80)
    
    return team_database

def build_team_name_mapping(all_teams):
    """Bouw een mapping voor variaties van team namen."""
    print("\n🔍 Bouwen van fuzzy matching database...")
    
    name_mapping = {}
    
    for team in all_teams:
        # Voeg verschillende variaties toe
        variations = [
            team,
            team.lower(),
            team.replace(' ', ''),
            team.replace('-', ' '),
            team.replace('FC', '').strip(),
            team.replace('AFC', '').strip(),
            team.replace('United', 'Utd').strip(),
            team.replace('City', '').strip()
        ]
        
        for variation in set(variations):
            name_mapping[variation] = team
    
    # Sla mapping op
    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'team_name_mapping.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(name_mapping, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Name mapping opgeslagen: {len(name_mapping)} variaties voor {len(all_teams)} teams")

if __name__ == "__main__":
    build_team_database()
