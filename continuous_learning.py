"""
🔄 CONTINUOUS LEARNING ENGINE 🔄
Haalt automatisch échte uitslagen op en traint AI ELKE DAG opnieuw!

Dit systeem:
1. Haalt dagelijks alle afgelopen wedstrijden op
2. Voegt ze toe aan training data
3. Retraint het model automatisch
4. Wordt ELKE DAG beter!
"""

import requests
import json
import os
import pickle
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

class ContinuousLearningEngine:
    """AI die zichzelf ELKE DAG verbetert!"""
    
    def __init__(self):
        self.api_football_key = "579ff3a56c73a8ffc2821f15c5cdebe8"
        
        # Data paths
        self.training_data_file = 'data/continuous_training_data.json'
        self.model_file = 'data/de_meester.pkl'
        self.stats_file = 'data/learning_stats.json'
        
        # Load existing data
        self.training_matches = self._load_training_data()
        self.learning_stats = self._load_stats()
        
        print("="*80)
        print("🔄 CONTINUOUS LEARNING ENGINE GEÏNITIALISEERD")
        print("="*80)
        print(f"   Huidige training data: {len(self.training_matches)} wedstrijden")
        print(f"   Laatste update: {self.learning_stats.get('last_update', 'Nooit')}")
        print("="*80)
    
    def fetch_yesterdays_results(self):
        """Haal alle afgelopen wedstrijden van gisteren op."""
        print(f"\n📥 OPHALEN GISTEREN'S RESULTATEN...")
        print("-" * 80)
        
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        new_matches = []
        
        # Eredivisie + Eerste Divisie
        leagues = {
            'Eredivisie': 88,
            'Eerste Divisie': 89
        }
        
        for league_name, league_id in leagues.items():
            try:
                url = "https://v3.football.api-sports.io/fixtures"
                headers = {
                    'x-rapidapi-key': self.api_football_key,
                    'x-rapidapi-host': 'v3.football.api-sports.io'
                }
                params = {
                    'league': league_id,
                    'season': 2024,
                    'date': yesterday,
                    'status': 'FT'  # Full Time
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    fixtures = data.get('response', [])
                    
                    print(f"   {league_name}: {len(fixtures)} wedstrijden")
                    
                    for fixture in fixtures:
                        match_data = {
                            'home_team': fixture['teams']['home']['name'],
                            'away_team': fixture['teams']['away']['name'],
                            'home_score': fixture['goals']['home'],
                            'away_score': fixture['goals']['away'],
                            'date': fixture['fixture']['date'],
                            'competition': league_name.lower().replace(' ', '_'),
                            'season': 2024,
                            'source': 'API-Football-Live',
                            'round': fixture.get('league', {}).get('round', 'Unknown')
                        }
                        
                        # Check if not already in training data
                        if not self._is_duplicate(match_data):
                            new_matches.append(match_data)
                            self.training_matches.append(match_data)
                
                time.sleep(1)  # Rate limiting
            
            except Exception as e:
                print(f"   ❌ Error {league_name}: {e}")
        
        print(f"\n✅ {len(new_matches)} NIEUWE wedstrijden toegevoegd!")
        return new_matches
    
    def _is_duplicate(self, match):
        """Check if match already exists in training data."""
        for existing in self.training_matches:
            if (existing['home_team'] == match['home_team'] and 
                existing['away_team'] == match['away_team'] and 
                existing['date'] == match['date']):
                return True
        return False
    
    def retrain_model(self):
        """Retrain het model met ALLE data (inclusief nieuwe!)."""
        print(f"\n🔄 RETRAINING MODEL MET {len(self.training_matches)} WEDSTRIJDEN...")
        print("="*80)
        
        if len(self.training_matches) < 100:
            print("⚠️  Te weinig data voor retraining (minimaal 100 wedstrijden)")
            return False
        
        # Prepare features (same as ultra_train_massive.py)
        X_home, X_away, y_home, y_away, feature_names = self._prepare_training_data()
        
        # Split
        X_home_train, X_home_test, y_home_train, y_home_test = train_test_split(
            X_home, y_home, test_size=0.2, random_state=42
        )
        X_away_train, X_away_test, y_away_train, y_away_test = train_test_split(
            X_away, y_away, test_size=0.2, random_state=42
        )
        
        # Scale
        scaler = StandardScaler()
        X_home_train_scaled = scaler.fit_transform(X_home_train)
        X_home_test_scaled = scaler.transform(X_home_test)
        X_away_train_scaled = scaler.transform(X_away_train)
        X_away_test_scaled = scaler.transform(X_away_test)
        
        print(f"\n🤖 Training {len(X_home_train)} samples...")
        
        # Train 5 models
        models = {}
        
        print("   1/5 Random Forest...", end=" ")
        rf_home = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        rf_away = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        rf_home.fit(X_home_train_scaled, y_home_train)
        rf_away.fit(X_away_train_scaled, y_away_train)
        models['random_forest'] = {'home': rf_home, 'away': rf_away}
        print("✅")
        
        print("   2/5 Gradient Boosting...", end=" ")
        gb_home = GradientBoostingRegressor(n_estimators=200, max_depth=7, learning_rate=0.1, random_state=42)
        gb_away = GradientBoostingRegressor(n_estimators=200, max_depth=7, learning_rate=0.1, random_state=42)
        gb_home.fit(X_home_train_scaled, y_home_train)
        gb_away.fit(X_away_train_scaled, y_away_train)
        models['gradient_boosting'] = {'home': gb_home, 'away': gb_away}
        print("✅")
        
        print("   3/5 Extra Trees...", end=" ")
        et_home = ExtraTreesRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        et_away = ExtraTreesRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        et_home.fit(X_home_train_scaled, y_home_train)
        et_away.fit(X_away_train_scaled, y_away_train)
        models['extra_trees'] = {'home': et_home, 'away': et_away}
        print("✅")
        
        print("   4/5 Ridge...", end=" ")
        ridge_home = Ridge(alpha=1.0, random_state=42)
        ridge_away = Ridge(alpha=1.0, random_state=42)
        ridge_home.fit(X_home_train_scaled, y_home_train)
        ridge_away.fit(X_away_train_scaled, y_away_train)
        models['ridge'] = {'home': ridge_home, 'away': ridge_away}
        print("✅")
        
        print("   5/5 Lasso...", end=" ")
        lasso_home = Lasso(alpha=0.1, random_state=42, max_iter=2000)
        lasso_away = Lasso(alpha=0.1, random_state=42, max_iter=2000)
        lasso_home.fit(X_home_train_scaled, y_home_train)
        lasso_away.fit(X_away_train_scaled, y_away_train)
        models['lasso'] = {'home': lasso_home, 'away': lasso_away}
        print("✅")
        
        # Evaluate
        weights = {
            'random_forest': 0.25,
            'gradient_boosting': 0.30,
            'extra_trees': 0.25,
            'ridge': 0.15,
            'lasso': 0.05
        }
        
        pred_home = np.zeros(len(X_home_test_scaled))
        pred_away = np.zeros(len(X_away_test_scaled))
        
        for model_name, weight in weights.items():
            pred_home += models[model_name]['home'].predict(X_home_test_scaled) * weight
            pred_away += models[model_name]['away'].predict(X_away_test_scaled) * weight
        
        # Calculate metrics
        mae_home = np.mean(np.abs(pred_home - y_home_test))
        mae_away = np.mean(np.abs(pred_away - y_away_test))
        
        pred_home_rounded = np.round(pred_home).astype(int)
        pred_away_rounded = np.round(pred_away).astype(int)
        exact_matches = np.sum((pred_home_rounded == y_home_test) & (pred_away_rounded == y_away_test))
        accuracy = (exact_matches / len(y_home_test)) * 100
        
        print(f"\n📊 NIEUWE PRESTATIES:")
        print(f"   MAE Thuis: {mae_home:.3f}")
        print(f"   MAE Uit: {mae_away:.3f}")
        print(f"   Exacte Scores: {accuracy:.1f}% ({exact_matches}/{len(y_home_test)})")
        
        # Compare with previous
        old_accuracy = self.learning_stats.get('accuracy', 0)
        improvement = accuracy - old_accuracy
        
        if improvement > 0:
            print(f"\n🎉 VERBETERING: +{improvement:.1f}% accuracy!")
        elif improvement < 0:
            print(f"\n⚠️  Verslechtering: {improvement:.1f}% (meer data nodig)")
        else:
            print(f"\n➡️  Gelijk gebleven")
        
        # Save model
        model_data = {
            'models': {
                'neural_network': {},
                'random_forest': models['random_forest'],
                'gradient_boosting': models['gradient_boosting'],
                'extra_trees': models['extra_trees'],
                'ridge': models['ridge'],
                'lasso': models['lasso']
            },
            'scaler': scaler,
            'feature_names': feature_names,
            'weights': weights,
            'accuracy': {
                'mae_home': mae_home,
                'mae_away': mae_away,
                'exact_score_accuracy': accuracy,
                'training_samples': len(X_home_train),
                'test_samples': len(X_home_test)
            },
            'learning_history': {
                'trained_at': datetime.now().isoformat(),
                'total_matches': len(self.training_matches),
                'eredivisie_matches': len([m for m in self.training_matches if 'eredivisie' in m['competition']]),
                'eerste_divisie_matches': len([m for m in self.training_matches if 'eerste_divisie' in m['competition']]),
                'improvement': improvement
            }
        }
        
        with open(self.model_file, 'wb') as f:
            pickle.dump(model_data, f)
        
        # Update stats
        self.learning_stats = {
            'last_update': datetime.now().isoformat(),
            'total_trainings': self.learning_stats.get('total_trainings', 0) + 1,
            'accuracy': accuracy,
            'total_matches': len(self.training_matches),
            'improvements': self.learning_stats.get('improvements', []) + [
                {'date': datetime.now().isoformat(), 'accuracy': accuracy, 'improvement': improvement}
            ]
        }
        
        print(f"\n💾 Model opgeslagen!")
        print("="*80)
        
        return True
    
    def _prepare_training_data(self):
        """Prepare training data (same as ultra_train_massive.py)."""
        # Team strengths database
        eredivisie_teams = {
            'PSV': 2.5, 'Feyenoord': 2.3, 'Ajax': 2.2, 'AZ': 2.0, 'FC Twente': 1.9,
            'FC Utrecht': 1.7, 'Fortuna Sittard': 1.3, 'Go Ahead Eagles': 1.4,
            'Heracles': 1.3, 'NEC': 1.5, 'PEC Zwolle': 1.4, 'RKC Waalwijk': 1.2,
            'Sparta Rotterdam': 1.5, 'SC Heerenveen': 1.4, 'FC Groningen': 1.3,
            'Willem II': 1.4, 'Almere City': 1.1, 'NAC Breda': 1.3
        }
        
        eerste_divisie_teams = {
            'FC Volendam': 1.8, 'ADO Den Haag': 1.7, 'Excelsior': 1.7,
            'NAC Breda': 1.6, 'De Graafschap': 1.6, 'Roda JC': 1.5,
            'FC Eindhoven': 1.5, 'Cambuur': 1.5, 'VVV-Venlo': 1.4,
            'Emmen': 1.4, 'FC Dordrecht': 1.3, 'MVV Maastricht': 1.3,
            'Helmond Sport': 1.3, 'TOP Oss': 1.2, 'Telstar': 1.2,
            'FC Den Bosch': 1.2, 'Jong Ajax': 1.4, 'Jong PSV': 1.3,
            'Jong AZ': 1.2, 'Jong FC Utrecht': 1.1
        }
        
        all_teams = {**eredivisie_teams, **eerste_divisie_teams}
        
        X_home = []
        X_away = []
        y_home = []
        y_away = []
        
        for match in self.training_matches:
            try:
                home_team = match['home_team']
                away_team = match['away_team']
                
                home_strength = all_teams.get(home_team, 1.3)
                away_strength = all_teams.get(away_team, 1.3)
                
                is_eredivisie = 'eredivisie' in match['competition']
                comp_modifier = 1.2 if is_eredivisie else 1.0
                
                # Generate 57 features (same as ultra training)
                features = {
                    'home_strength': home_strength * comp_modifier,
                    'away_strength': away_strength * comp_modifier,
                    'strength_diff': (home_strength - away_strength) * comp_modifier,
                    'strength_ratio': home_strength / max(away_strength, 0.1),
                    'home_attack': home_strength * 1.2,
                    'home_defense': 2.5 - home_strength,
                    'away_attack': away_strength * 1.0,
                    'away_defense': 2.5 - away_strength,
                    'home_attack_vs_away_defense': (home_strength * 1.2) - (2.5 - away_strength),
                    'away_attack_vs_home_defense': (away_strength * 1.0) - (2.5 - home_strength),
                    'home_advantage': 0.3,
                    'away_disadvantage': -0.2,
                    'is_eredivisie': 1.0 if is_eredivisie else 0.0,
                    'is_eerste_divisie': 0.0 if is_eredivisie else 1.0,
                    'competition_level': 2.0 if is_eredivisie else 1.5,
                    'home_win_rate': min(0.9, home_strength / 2.5),
                    'away_win_rate': min(0.9, away_strength / 2.5),
                    'draw_probability': 0.3,
                    'expected_total_goals': home_strength + away_strength,
                    'expected_goal_diff': home_strength - away_strength + 0.3,
                    'home_form': home_strength * np.random.uniform(0.8, 1.2),
                    'away_form': away_strength * np.random.uniform(0.8, 1.2),
                    'home_motivation': 1.1,
                    'away_motivation': 1.0,
                    'home_shots_expected': home_strength * 10,
                    'away_shots_expected': away_strength * 8,
                    'home_possession_expected': 50 + (home_strength - away_strength) * 10,
                    'away_possession_expected': 50 - (home_strength - away_strength) * 10,
                    'strength_product': home_strength * away_strength,
                    'strength_sum': home_strength + away_strength,
                    'attack_sum': (home_strength * 1.2) + away_strength,
                    'defense_sum': (2.5 - home_strength) + (2.5 - away_strength),
                    'home_strength_squared': home_strength ** 2,
                    'away_strength_squared': away_strength ** 2,
                    'strength_diff_squared': (home_strength - away_strength) ** 2,
                    'both_top_teams': 1.0 if (home_strength > 2.0 and away_strength > 2.0) else 0.0,
                    'both_bottom_teams': 1.0 if (home_strength < 1.3 and away_strength < 1.3) else 0.0,
                    'mismatch': 1.0 if abs(home_strength - away_strength) > 0.8 else 0.0,
                    'home_consistency': home_strength * 0.9,
                    'away_consistency': away_strength * 0.9,
                    'match_importance': 0.8,
                    'weather_factor': 1.0,
                    'referee_factor': 1.0,
                    'attack_defense_home': (home_strength * 1.2) * (2.5 - away_strength),
                    'attack_defense_away': (away_strength * 1.0) * (2.5 - home_strength),
                    'form_diff': 0.0,
                    'momentum_home': home_strength * 0.1,
                    'momentum_away': away_strength * 0.1,
                    'variance_home': home_strength * 0.2,
                    'variance_away': away_strength * 0.2,
                    'skewness_factor': 0.0,
                    'kurtosis_factor': 0.0,
                    'prediction_confidence_base': min(0.9, abs(home_strength - away_strength) / 2),
                    'match_volatility': 1.0 - (abs(home_strength - away_strength) / 2),
                    'upset_potential': max(0, away_strength - home_strength),
                    'home_is_jong': 0.8 if 'Jong' in home_team else 1.0,
                    'away_is_jong': 0.8 if 'Jong' in away_team else 1.0,
                }
                
                feature_vector = list(features.values())
                
                X_home.append(feature_vector)
                X_away.append(feature_vector)
                y_home.append(match['home_score'])
                y_away.append(match['away_score'])
            
            except:
                continue
        
        return np.array(X_home), np.array(X_away), np.array(y_home), np.array(y_away), list(features.keys())
    
    def _load_training_data(self):
        """Load existing training data."""
        if os.path.exists(self.training_data_file):
            with open(self.training_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_training_data(self):
        """Save training data."""
        os.makedirs(os.path.dirname(self.training_data_file), exist_ok=True)
        with open(self.training_data_file, 'w', encoding='utf-8') as f:
            json.dump(self.training_matches, f, indent=2, ensure_ascii=False)
    
    def _load_stats(self):
        """Load learning stats."""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_stats(self):
        """Save learning stats."""
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        with open(self.stats_file, 'w') as f:
            json.dump(self.learning_stats, f, indent=2)
    
    def daily_update(self):
        """Voer dagelijkse update uit: haal nieuwe data + retrain."""
        print("\n" + "="*80)
        print("🔄 DAGELIJKSE CONTINUOUS LEARNING UPDATE")
        print("="*80)
        
        # 1. Fetch new results
        new_matches = self.fetch_yesterdays_results()
        
        if len(new_matches) == 0:
            print("\n⚠️  Geen nieuwe wedstrijden - skip retraining")
            return False
        
        # 2. Save new data
        self._save_training_data()
        print(f"\n💾 Training data opgeslagen ({len(self.training_matches)} totaal)")
        
        # 3. Retrain model
        success = self.retrain_model()
        
        if success:
            self._save_stats()
            print(f"\n✅ CONTINUOUS LEARNING COMPLEET!")
            print(f"   Totaal trainingen: {self.learning_stats['total_trainings']}")
            print(f"   Huidige accuracy: {self.learning_stats['accuracy']:.1f}%")
        
        print("="*80)
        return success


if __name__ == "__main__":
    engine = ContinuousLearningEngine()
    engine.daily_update()
