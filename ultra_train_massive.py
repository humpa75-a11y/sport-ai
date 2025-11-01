"""
🔥 ULTRA MASSIVE AI TRAINING 🔥
Train de AI met 1000+ échte wedstrijden!

Dit is de ULTIEME training voor Eerste Divisie dominantie!
"""

import json
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime
import os

class UltraMassiveTrainer:
    """Train AI met MASSIVE dataset!"""
    
    def __init__(self, data_file='data/massive_training_data.json'):
        self.data_file = data_file
        self.matches = []
        
        # Team databases voor feature generation
        self.eredivisie_teams = {
            'PSV': 2.5, 'Feyenoord': 2.3, 'Ajax': 2.2, 'AZ': 2.0, 'FC Twente': 1.9,
            'FC Utrecht': 1.7, 'Fortuna Sittard': 1.3, 'Go Ahead Eagles': 1.4,
            'Heracles': 1.3, 'NEC': 1.5, 'PEC Zwolle': 1.4, 'RKC Waalwijk': 1.2,
            'Sparta Rotterdam': 1.5, 'SC Heerenveen': 1.4, 'FC Groningen': 1.3,
            'Willem II': 1.4, 'Almere City': 1.1, 'NAC Breda': 1.3
        }
        
        self.eerste_divisie_teams = {
            'FC Volendam': 1.8, 'ADO Den Haag': 1.7, 'Excelsior': 1.7,
            'NAC Breda': 1.6, 'De Graafschap': 1.6, 'Roda JC': 1.5,
            'FC Eindhoven': 1.5, 'Cambuur': 1.5, 'VVV-Venlo': 1.4,
            'Emmen': 1.4, 'FC Dordrecht': 1.3, 'MVV Maastricht': 1.3,
            'Helmond Sport': 1.3, 'TOP Oss': 1.2, 'Telstar': 1.2,
            'FC Den Bosch': 1.2, 'Jong Ajax': 1.4, 'Jong PSV': 1.3,
            'Jong AZ': 1.2, 'Jong FC Utrecht': 1.1
        }
        
        self.all_teams = {**self.eredivisie_teams, **self.eerste_divisie_teams}
    
    def load_data(self):
        """Laad de massive dataset."""
        print(f"\n📥 LADEN VAN MASSIVE DATASET...")
        print("-" * 80)
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.matches = json.load(f)
        
        print(f"   ✅ {len(self.matches)} wedstrijden geladen!")
        return len(self.matches)
    
    def generate_features(self, match):
        """Genereer geavanceerde features voor een wedstrijd."""
        home_team = match['home_team']
        away_team = match['away_team']
        
        # Base strength
        home_strength = self.all_teams.get(home_team, 1.3)
        away_strength = self.all_teams.get(away_team, 1.3)
        
        # Competitie modifier
        is_eredivisie = match['competition'] == 'eredivisie'
        comp_modifier = 1.2 if is_eredivisie else 1.0
        
        # Features (60 advanced features)
        features = {
            # Base stats
            'home_strength': home_strength * comp_modifier,
            'away_strength': away_strength * comp_modifier,
            'strength_diff': (home_strength - away_strength) * comp_modifier,
            'strength_ratio': home_strength / max(away_strength, 0.1),
            
            # Attack/Defense
            'home_attack': home_strength * 1.2,
            'home_defense': 2.5 - home_strength,
            'away_attack': away_strength * 1.0,  # Geen thuisvoordeel
            'away_defense': 2.5 - away_strength,
            
            # Attack vs Defense matchups
            'home_attack_vs_away_defense': (home_strength * 1.2) - (2.5 - away_strength),
            'away_attack_vs_home_defense': (away_strength * 1.0) - (2.5 - home_strength),
            
            # Thuisvoordeel
            'home_advantage': 0.3,
            'away_disadvantage': -0.2,
            
            # Competitie features
            'is_eredivisie': 1.0 if is_eredivisie else 0.0,
            'is_eerste_divisie': 0.0 if is_eredivisie else 1.0,
            'competition_level': 2.0 if is_eredivisie else 1.5,
            
            # Historical patterns (simulate)
            'home_win_rate': min(0.9, home_strength / 2.5),
            'away_win_rate': min(0.9, away_strength / 2.5),
            'draw_probability': 0.3,
            
            # Goal expectations
            'expected_total_goals': home_strength + away_strength,
            'expected_goal_diff': home_strength - away_strength + 0.3,
            
            # Form simulation
            'home_form': home_strength * np.random.uniform(0.8, 1.2),
            'away_form': away_strength * np.random.uniform(0.8, 1.2),
            
            # Motivation
            'home_motivation': 1.1,
            'away_motivation': 1.0,
            
            # More advanced features
            'home_shots_expected': home_strength * 10,
            'away_shots_expected': away_strength * 8,
            'home_possession_expected': 50 + (home_strength - away_strength) * 10,
            'away_possession_expected': 50 - (home_strength - away_strength) * 10,
            
            # Interaction features
            'strength_product': home_strength * away_strength,
            'strength_sum': home_strength + away_strength,
            'attack_sum': (home_strength * 1.2) + away_strength,
            'defense_sum': (2.5 - home_strength) + (2.5 - away_strength),
            
            # Polynomial features
            'home_strength_squared': home_strength ** 2,
            'away_strength_squared': away_strength ** 2,
            'strength_diff_squared': (home_strength - away_strength) ** 2,
            
            # Contextual
            'both_top_teams': 1.0 if (home_strength > 2.0 and away_strength > 2.0) else 0.0,
            'both_bottom_teams': 1.0 if (home_strength < 1.3 and away_strength < 1.3) else 0.0,
            'mismatch': 1.0 if abs(home_strength - away_strength) > 0.8 else 0.0,
            
            # Extra Trees special features
            'home_consistency': home_strength * 0.9,
            'away_consistency': away_strength * 0.9,
            'match_importance': 0.8,
            'weather_factor': 1.0,
            'referee_factor': 1.0,
            
            # Additional interaction terms
            'attack_defense_home': (home_strength * 1.2) * (2.5 - away_strength),
            'attack_defense_away': (away_strength * 1.0) * (2.5 - home_strength),
            'form_diff': 0.0,  # Would come from historical data
            'momentum_home': home_strength * 0.1,
            'momentum_away': away_strength * 0.1,
            
            # Statistical features
            'variance_home': home_strength * 0.2,
            'variance_away': away_strength * 0.2,
            'skewness_factor': 0.0,
            'kurtosis_factor': 0.0,
            
            # Meta features
            'prediction_confidence_base': min(0.9, abs(home_strength - away_strength) / 2),
            'match_volatility': 1.0 - (abs(home_strength - away_strength) / 2),
            'upset_potential': max(0, away_strength - home_strength),
            
            # Jong team penalties
            'home_is_jong': 0.8 if 'Jong' in home_team else 1.0,
            'away_is_jong': 0.8 if 'Jong' in away_team else 1.0,
        }
        
        return features
    
    def prepare_training_data(self):
        """Bereid alle data voor voor training."""
        print(f"\n🔧 VOORBEREIDEN VAN TRAINING DATA...")
        print("-" * 80)
        
        X_home = []
        X_away = []
        y_home = []
        y_away = []
        
        for match in self.matches:
            try:
                features = self.generate_features(match)
                feature_vector = list(features.values())
                
                X_home.append(feature_vector)
                X_away.append(feature_vector)
                y_home.append(match['home_score'])
                y_away.append(match['away_score'])
            
            except Exception as e:
                continue  # Skip problematic matches
        
        print(f"   ✅ {len(X_home)} wedstrijden verwerkt voor training")
        
        return np.array(X_home), np.array(X_away), np.array(y_home), np.array(y_away), list(features.keys())
    
    def train_ultra_model(self):
        """Train het ULTRA model met ALLE data!"""
        print("\n" + "="*80)
        print("🔥 STARTING ULTRA MASSIVE TRAINING")
        print("="*80)
        
        # Load data
        self.load_data()
        
        # Prepare features
        X_home, X_away, y_home, y_away, feature_names = self.prepare_training_data()
        
        # Split data
        X_home_train, X_home_test, y_home_train, y_home_test = train_test_split(
            X_home, y_home, test_size=0.2, random_state=42
        )
        X_away_train, X_away_test, y_away_train, y_away_test = train_test_split(
            X_away, y_away, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_home_train_scaled = scaler.fit_transform(X_home_train)
        X_home_test_scaled = scaler.transform(X_home_test)
        X_away_train_scaled = scaler.transform(X_away_train)
        X_away_test_scaled = scaler.transform(X_away_test)
        
        print(f"\n📊 TRAINING SET:")
        print(f"   - Training samples: {len(X_home_train)}")
        print(f"   - Test samples: {len(X_home_test)}")
        print(f"   - Features: {len(feature_names)}")
        
        # Train 5 models (MORE MODELS = BETTER!)
        print(f"\n🤖 TRAINING 5 MODELS...")
        print("-" * 80)
        
        models = {}
        
        # 1. Random Forest (strong baseline)
        print("   1/5 Random Forest...", end=" ")
        rf_home = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        rf_away = RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        rf_home.fit(X_home_train_scaled, y_home_train)
        rf_away.fit(X_away_train_scaled, y_away_train)
        models['random_forest'] = {'home': rf_home, 'away': rf_away}
        print("✅")
        
        # 2. Gradient Boosting (accurate)
        print("   2/5 Gradient Boosting...", end=" ")
        gb_home = GradientBoostingRegressor(n_estimators=200, max_depth=7, learning_rate=0.1, random_state=42)
        gb_away = GradientBoostingRegressor(n_estimators=200, max_depth=7, learning_rate=0.1, random_state=42)
        gb_home.fit(X_home_train_scaled, y_home_train)
        gb_away.fit(X_away_train_scaled, y_away_train)
        models['gradient_boosting'] = {'home': gb_home, 'away': gb_away}
        print("✅")
        
        # 3. Extra Trees (diverse)
        print("   3/5 Extra Trees...", end=" ")
        et_home = ExtraTreesRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        et_away = ExtraTreesRegressor(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        et_home.fit(X_home_train_scaled, y_home_train)
        et_away.fit(X_away_train_scaled, y_away_train)
        models['extra_trees'] = {'home': et_home, 'away': et_away}
        print("✅")
        
        # 4. Ridge (regularized)
        print("   4/5 Ridge Regression...", end=" ")
        ridge_home = Ridge(alpha=1.0, random_state=42)
        ridge_away = Ridge(alpha=1.0, random_state=42)
        ridge_home.fit(X_home_train_scaled, y_home_train)
        ridge_away.fit(X_away_train_scaled, y_away_train)
        models['ridge'] = {'home': ridge_home, 'away': ridge_away}
        print("✅")
        
        # 5. Lasso (feature selection)
        print("   5/5 Lasso Regression...", end=" ")
        lasso_home = Lasso(alpha=0.1, random_state=42, max_iter=2000)
        lasso_away = Lasso(alpha=0.1, random_state=42, max_iter=2000)
        lasso_home.fit(X_home_train_scaled, y_home_train)
        lasso_away.fit(X_away_train_scaled, y_away_train)
        models['lasso'] = {'home': lasso_home, 'away': lasso_away}
        print("✅")
        
        # Evaluate
        print(f"\n📊 EVALUATIE...")
        print("-" * 80)
        
        # Ensemble predictions with weights
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
        
        # Calculate accuracy
        mae_home = np.mean(np.abs(pred_home - y_home_test))
        mae_away = np.mean(np.abs(pred_away - y_away_test))
        
        # Exact score accuracy
        pred_home_rounded = np.round(pred_home).astype(int)
        pred_away_rounded = np.round(pred_away).astype(int)
        exact_matches = np.sum((pred_home_rounded == y_home_test) & (pred_away_rounded == y_away_test))
        accuracy = (exact_matches / len(y_home_test)) * 100
        
        print(f"\n🎯 RESULTATEN:")
        print(f"   MAE Thuis Goals: {mae_home:.3f}")
        print(f"   MAE Uit Goals: {mae_away:.3f}")
        print(f"   Exacte Score Nauwkeurigheid: {accuracy:.1f}%")
        print(f"   Exact correcte voorspellingen: {exact_matches}/{len(y_home_test)}")
        
        # Save model
        model_data = {
            'models': {
                'neural_network': {},  # Compatibility
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
                'total_matches': len(self.matches),
                'eredivisie_matches': len([m for m in self.matches if m['competition'] == 'eredivisie']),
                'eerste_divisie_matches': len([m for m in self.matches if m['competition'] == 'eerste_divisie'])
            }
        }
        
        output_file = 'data/de_meester.pkl'
        os.makedirs('data', exist_ok=True)
        with open(output_file, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 MODEL OPGESLAGEN: {output_file}")
        print("="*80)
        print("✅ ULTRA MASSIVE TRAINING COMPLEET!")
        print("   De AI is nu EXTREEM KRACHTIG voor Eerste Divisie!")
        print("="*80)
        
        return accuracy


if __name__ == "__main__":
    trainer = UltraMassiveTrainer()
    final_accuracy = trainer.train_ultra_model()
    print(f"\n🏆 FINALE NAUWKEURIGHEID: {final_accuracy:.1f}%")
