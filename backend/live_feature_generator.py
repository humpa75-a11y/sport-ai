"""
⚡ LIVE FEATURE GENERATOR - Real-Time Intelligentie ⚡

Dit script genereert echte features voor wedstrijden op basis van:
- Team database
- Recente vorm
- Head-to-head geschiedenis
- Thuisvoordeel
"""

import json
import os
from difflib import get_close_matches
import pandas as pd

class LiveFeatureGenerator:
    """Genereert real-time features voor voorspellingen."""
    
    def __init__(self):
        """Laad de team database en name mapping."""
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        # Laad team database
        db_path = os.path.join(data_dir, 'team_database.json')
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                self.team_db = json.load(f)
            print(f"✅ Team database geladen: {len(self.team_db)} teams")
        else:
            self.team_db = {}
            print("⚠️ Geen team database gevonden")
        
        # Laad name mapping
        mapping_path = os.path.join(data_dir, 'team_name_mapping.json')
        if os.path.exists(mapping_path):
            with open(mapping_path, 'r', encoding='utf-8') as f:
                self.name_mapping = json.load(f)
            print(f"✅ Name mapping geladen: {len(self.name_mapping)} variaties")
        else:
            self.name_mapping = {}
            print("⚠️ Geen name mapping gevonden")
    
    def find_team(self, team_name):
        """Vind een team met fuzzy matching."""
        # Direct match
        if team_name in self.team_db:
            return team_name
        
        # Check mapping
        if team_name in self.name_mapping:
            canonical_name = self.name_mapping[team_name]
            if canonical_name in self.team_db:
                return canonical_name
        
        # Fuzzy match
        all_teams = list(self.team_db.keys())
        matches = get_close_matches(team_name, all_teams, n=1, cutoff=0.6)
        if matches:
            return matches[0]
        
        return None
    
    def generate_features(self, home_team, away_team, speelronde=19):
        """Genereer features voor een wedstrijd."""
        
        # Vind teams
        home_canonical = self.find_team(home_team)
        away_canonical = self.find_team(away_team)
        
        if not home_canonical or not away_canonical:
            print(f"⚠️ Team niet gevonden: {home_team if not home_canonical else away_team}")
            print(f"   💡 Using SMART defaults met team analyse...")
            return self._get_default_features(home_team, away_team)
        
        print(f"✅ Match gevonden: {home_team} -> {home_canonical}")
        print(f"✅ Match gevonden: {away_team} -> {away_canonical}")
        
        home_data = self.team_db[home_canonical]
        away_data = self.team_db[away_canonical]
        
        # Extract home en away specifieke stats
        home_stats = home_data['home_stats']
        away_stats = away_data['away_stats']

        # 🧠 NIEUW V3: Matchday Pressure
        # Hoe verder in het seizoen, hoe hoger de druk.
        # We gebruiken een kwadratische schaal voor non-lineaire druktoename.
        # Max speelrondes in de meeste competities is 38.
        matchday_pressure = min((speelronde / 38.0) ** 2, 1.5) # Cap op 1.5

        # 🔥 NIEUW V3: Goal Difference Momentum & H2H Dominance
        h2h_stats = home_data.get('h2h', {}).get(away_canonical, {})
        goal_diff_momentum = h2h_stats.get('goal_diff_momentum', 0)
        h2h_dominance_score = h2h_stats.get('dominance_score', 0.5) # Default 0.5 (neutraal)
        
        # Bouw features dictionary
        features = {
            # Basis odds (geschat op basis van vorm)
            'odds_home': self._estimate_odds(home_stats['form_score'], away_stats['form_score'], 'home'),
            'odds_draw': 3.5,  # Gemiddelde
            'odds_away': self._estimate_odds(home_stats['form_score'], away_stats['form_score'], 'away'),
            
            # Implied probabilities
            'implied_prob_home': 1 / self._estimate_odds(home_stats['form_score'], away_stats['form_score'], 'home'),
            'implied_prob_draw': 1 / 3.5,
            'implied_prob_away': 1 / self._estimate_odds(home_stats['form_score'], away_stats['form_score'], 'away'),
            
            # Schoten (geschat)
            'home_shots': home_stats['avg_goals_scored'] * 6,  # Ruwe schatting
            'away_shots': away_stats['avg_goals_scored'] * 6,
            'home_shots_target': home_stats['avg_goals_scored'] * 3,
            'away_shots_target': away_stats['avg_goals_scored'] * 3,
            'shot_accuracy_home': 0.5 if home_stats['avg_goals_scored'] == 0 else min(home_stats['avg_goals_scored'] / 3, 1.0),
            'shot_accuracy_away': 0.5 if away_stats['avg_goals_scored'] == 0 else min(away_stats['avg_goals_scored'] / 3, 1.0),
            
            # Fouls en kaarten (geschat)
            'home_fouls': 10,
            'away_fouls': 10,
            'home_yellow': 2,
            'away_yellow': 2,
            'home_red': 0,
            'away_red': 0,
            'discipline_diff': 0,
            
            # Corners (geschat)
            'home_corners': home_stats['avg_goals_scored'] * 2,
            'away_corners': away_stats['avg_goals_scored'] * 2,
            'corner_diff': (home_stats['avg_goals_scored'] - away_stats['avg_goals_scored']) * 2,
            
            # ECHTE DATA - Recent Form (laatste 5 wedstrijden)
            'home_avg_goals_scored_5': home_stats['last_5_goals_scored'] / min(home_stats['total_games'], 5),
            'home_avg_goals_conceded_5': home_stats['last_5_goals_conceded'] / min(home_stats['total_games'], 5),
            'away_avg_goals_scored_5': away_stats['last_5_goals_scored'] / min(away_stats['total_games'], 5),
            'away_avg_goals_conceded_5': away_stats['last_5_goals_conceded'] / min(away_stats['total_games'], 5),
            
            # ECHTE DATA - Overall stats
            'home_win_rate': home_stats['win_rate'],
            'away_win_rate': away_stats['win_rate'],
            
            # ECHTE DATA - Attack & Defense Strength
            'home_attack_strength': home_stats['attack_strength'],
            'home_defense_strength': home_stats['defense_strength'],
            'away_attack_strength': away_stats['attack_strength'],
            'away_defense_strength': away_stats['defense_strength'],
            
            # ECHTE DATA - Attack vs Defense matchup
            'attack_vs_defense_home': home_stats['attack_strength'] / max(away_stats['defense_strength'], 0.5),
            'attack_vs_defense_away': away_stats['attack_strength'] / max(home_stats['defense_strength'], 0.5),
            
            # V2 Features
            'ref_avg_cards': 4.0,  # Gemiddelde
            'home_avg_goals_1H': home_stats['last_5_goals_scored'] / min(home_stats['total_games'], 5) * 0.45,
            'away_avg_goals_1H': away_stats['last_5_goals_scored'] / min(away_stats['total_games'], 5) * 0.45,
            'home_avg_goals_2H': home_stats['last_5_goals_scored'] / min(home_stats['total_games'], 5) * 0.55,
            'away_avg_goals_2H': away_stats['last_5_goals_scored'] / min(away_stats['total_games'], 5) * 0.55,
            'home_2H_strength': home_stats['form_score'],

            # 🔥 V3 ADVANCED FEATURES 🔥
            'goal_diff_momentum': goal_diff_momentum,
            'h2h_dominance_score': h2h_dominance_score,
            'matchday_pressure': matchday_pressure
        }
        
        return features
    
    def _estimate_odds(self, home_form, away_form, result_type):
        """Schat odds op basis van vorm."""
        if result_type == 'home':
            strength_diff = home_form - away_form
            base_odds = 2.0
            return max(1.5, base_odds - (strength_diff * 0.3))
        else:  # away
            strength_diff = away_form - home_form
            base_odds = 3.5
            return max(2.0, base_odds - (strength_diff * 0.3))
    
    def _get_default_features(self, home_team=None, away_team=None):
        """SMART fallback met team naam analyse voor betere variatie."""
        import random
        
        # Analyse team namen voor rough estimates
        home_is_jong = home_team and 'Jong' in home_team
        away_is_jong = away_team and 'Jong' in away_team
        
        # Jong teams: jonger, aanvallender, meer goals maar ook meer tegen
        home_boost = 1.15 if home_is_jong else 1.0
        away_boost = 1.15 if away_is_jong else 1.0
        
        # Randomness voor variatie (±15%)
        home_var = random.uniform(0.88, 1.12)
        away_var = random.uniform(0.88, 1.12)
        
        # Eerste Divisie boost (meer goals dan Eredivisie gemiddeld)
        ed_boost = 1.12
        
        home_att = round((1.75 * home_boost * home_var * ed_boost), 2)
        away_att = round((1.55 * away_boost * away_var * ed_boost), 2)
        home_wr = min(0.65, max(0.35, 0.48 * home_var))
        away_wr = min(0.55, max(0.25, 0.38 * away_var))
        
        return {
            'odds_home': round(max(1.5, min(4.5, 2.10 / home_var)), 2),
            'odds_draw': 3.40,
            'odds_away': round(max(1.8, min(5.0, 3.20 / away_var)), 2),
            'implied_prob_home': home_wr,
            'implied_prob_draw': 0.294,
            'implied_prob_away': away_wr,
            'home_shots': round(14 * home_boost, 1),
            'away_shots': round(10 * away_boost, 1),
            'home_shots_target': round(6 * home_boost, 1),
            'away_shots_target': round(4 * away_boost, 1),
            'shot_accuracy_home': min(0.52, 0.43 * home_boost),
            'shot_accuracy_away': min(0.52, 0.40 * away_boost),
            'home_avg_goals_scored_5': home_att,
            'away_avg_goals_scored_5': away_att,
            'home_avg_goals_conceded_5': round(1.15 * away_var * ed_boost, 2),
            'away_avg_goals_conceded_5': round(1.35 * home_var * ed_boost, 2),
            'home_attack_strength': home_att,
            'away_attack_strength': away_att,
            'home_defense_strength': max(0.6, round(1.90 / home_boost, 2)),
            'away_defense_strength': max(0.6, round(2.10 / away_boost, 2)),
            'home_win_rate': home_wr,
            'away_win_rate': away_wr,
            'home_home_advantage': 0.6,
            'away_away_form': 0.4,
            'home_fouls': 10,
            'away_fouls': 10,
            'home_yellow': 2,
            'away_yellow': 2,
            'home_red': 0,
            'away_red': 0,
            'discipline_diff': 0,
            'home_corners': round(5 * home_boost, 1),
            'away_corners': round(4 * away_boost, 1),
            'corner_diff': round((5 * home_boost) - (4 * away_boost), 1),
            'attack_vs_defense_home': round(home_att / max(0.6, 2.10 / away_boost), 2),
            'attack_vs_defense_away': round(away_att / max(0.6, 1.90 / home_boost), 2),
            'ref_avg_cards': 4.0,
            'home_avg_goals_1H': round(home_att * 0.45, 2),
            'away_avg_goals_1H': round(away_att * 0.45, 2),
            'home_avg_goals_2H': round(home_att * 0.55, 2),
            'away_avg_goals_2H': round(away_att * 0.55, 2),
            'home_2H_strength': round(1.5 * home_boost, 2),
            # V3 Defaults
            'goal_diff_momentum': 0,
            'h2h_dominance_score': 0.5,
            'matchday_pressure': 0.25 # Mid-season pressure
        }

if __name__ == "__main__":
    # Test
    generator = LiveFeatureGenerator()
    
    print("\n" + "="*80)
    print("🧪 TEST: Real Madrid vs Barcelona")
    print("="*80)
    features = generator.generate_features("Real Madrid", "Barcelona")
    print(f"\n📊 Gegenereerde Features:")
    for key, value in list(features.items())[:10]:
        print(f"   {key}: {value}")
    print(f"   ... en {len(features) - 10} meer features")
