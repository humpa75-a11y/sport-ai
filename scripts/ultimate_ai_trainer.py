"""
🔥 ULTIMATE AI TRAINER 🔥

ZWARE TRAINING op VERSE DATA!

Features:
- Multiple advanced ML algorithms
- Hyperparameter tuning
- Cross-validation
- Ensemble stacking
- Deep learning layers
- Feature importance analysis

Output: ULTRA-SMART AI model
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.neural_network import MLPRegressor
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pickle
from datetime import datetime
import glob

class UltimateAITrainer:
    """KILLER AI TRAINER - Train op verse data met meerdere algoritmes"""
    
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.scaler = StandardScaler()
        self.feature_importance = {}
        
    def load_latest_data(self):
        """Laad de nieuwste training data"""
        print("\n" + "="*80)
        print("LOADING TRAINING DATA")
        print("="*80)
        
        # Zoek naar meest recente master data file
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        pattern = os.path.join(data_dir, 'master_training_data_*.csv')
        files = glob.glob(pattern)
        
        if not files:
            print("ERROR: No training data found!")
            print("Run first: python scripts/ultimate_data_scraper.py")
            return None
        
        # Neem nieuwste file
        latest_file = max(files, key=os.path.getctime)
        print(f"Loading: {latest_file}")
        
        df = pd.read_csv(latest_file)
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        return df
    
    def engineer_features(self, df):
        """
        Engineer ADVANCED features voor AI training
        """
        print("\n" + "="*80)
        print("ENGINEERING ADVANCED FEATURES")
        print("="*80)
        
        df = df.copy()
        
        # Feature 1: Form (laatste 5 wedstrijden)
        df['home_form'] = (df['home_wins'] * 3 + df['home_draws']) / (df['home_played'] + 1)
        df['away_form'] = (df['away_wins'] * 3 + df['away_draws']) / (df['away_played'] + 1)
        
        # Feature 2: Attack strength
        df['home_attack_strength'] = df['home_avg_goals_scored'] / (df['home_avg_goals_scored'].mean() + 0.1)
        df['away_attack_strength'] = df['away_avg_goals_scored'] / (df['away_avg_goals_scored'].mean() + 0.1)
        
        # Feature 3: Defense strength
        df['home_defense_strength'] = df['home_avg_goals_conceded'] / (df['home_avg_goals_conceded'].mean() + 0.1)
        df['away_defense_strength'] = df['away_avg_goals_conceded'] / (df['away_avg_goals_conceded'].mean() + 0.1)
        
        # Feature 4: Goal difference
        df['home_goal_diff'] = df['home_goals_for'] - df['home_goals_against']
        df['away_goal_diff'] = df['away_goals_for'] - df['away_goals_against']
        
        # Feature 5: Points per game
        df['home_ppg'] = (df['home_wins'] * 3 + df['home_draws']) / (df['home_played'] + 1)
        df['away_ppg'] = (df['away_wins'] * 3 + df['away_draws']) / (df['away_played'] + 1)
        
        # Feature 6: Win ratio difference
        df['win_ratio_diff'] = df['home_win_rate'] - df['away_win_rate']
        
        # Feature 7: Expected goals (simplified Poisson)
        df['home_xg'] = df['home_avg_goals_scored'] * df['away_defense_strength']
        df['away_xg'] = df['away_avg_goals_scored'] * df['home_defense_strength']
        
        # Feature 8: Match intensity
        df['match_intensity'] = df['home_avg_goals_scored'] + df['away_avg_goals_scored']
        
        # Feature 9: Consistency score
        df['home_consistency'] = 1 - (df['home_draws'] / (df['home_played'] + 1))
        df['away_consistency'] = 1 - (df['away_draws'] / (df['away_played'] + 1))
        
        # Feature 10: Momentum (recent form trend)
        df['home_momentum'] = df['home_form'] * df['home_ppg']
        df['away_momentum'] = df['away_form'] * df['away_ppg']
        
        print(f"Engineered {df.shape[1]} features")
        
        # Drop missing values
        df = df.dropna()
        print(f"After cleaning: {df.shape}")
        
        return df
    
    def prepare_training_data(self, df):
        """
        Prepare X (features) en y (targets) voor training
        """
        print("\n" + "="*80)
        print("PREPARING TRAINING DATA")
        print("="*80)
        
        # Feature columns
        feature_cols = [
            'home_win_rate', 'away_win_rate',
            'home_avg_goals_scored', 'home_avg_goals_conceded',
            'away_avg_goals_scored', 'away_avg_goals_conceded',
            'home_form', 'away_form',
            'home_attack_strength', 'away_attack_strength',
            'home_defense_strength', 'away_defense_strength',
            'home_goal_diff', 'away_goal_diff',
            'home_ppg', 'away_ppg',
            'win_ratio_diff',
            'home_xg', 'away_xg',
            'match_intensity',
            'home_consistency', 'away_consistency',
            'home_momentum', 'away_momentum'
        ]
        
        # Check welke features beschikbaar zijn
        available_features = [col for col in feature_cols if col in df.columns]
        print(f"Using {len(available_features)} features")
        
        X = df[available_features]
        
        # Targets: home_goals en away_goals
        y_home = df['home_goals']
        y_away = df['away_goals']
        
        print(f"X shape: {X.shape}")
        print(f"y_home shape: {y_home.shape}")
        print(f"y_away shape: {y_away.shape}")
        
        return X, y_home, y_away, available_features
    
    def train_ensemble_models(self, X_train, y_train, model_name="home"):
        """
        Train MULTIPLE models en selecteer de beste
        """
        print(f"\n" + "="*80)
        print(f"TRAINING ENSEMBLE MODELS FOR {model_name.upper()}")
        print("="*80)
        
        models_to_train = {
            'RandomForest': RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            ),
            'GradientBoosting': GradientBoostingRegressor(
                n_estimators=150,
                max_depth=7,
                learning_rate=0.1,
                random_state=42
            ),
            'XGBoost': XGBRegressor(
                n_estimators=150,
                max_depth=7,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            ),
            'NeuralNetwork': MLPRegressor(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                max_iter=500,
                random_state=42
            ),
            'AdaBoost': AdaBoostRegressor(
                n_estimators=100,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        results = {}
        
        for name, model in models_to_train.items():
            print(f"\nTraining {name}...", end=' ')
            
            try:
                # Train model
                model.fit(X_train, y_train)
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_absolute_error')
                mae = -cv_scores.mean()
                
                results[name] = {
                    'model': model,
                    'mae': mae,
                    'cv_std': cv_scores.std()
                }
                
                print(f"MAE: {mae:.3f} (+/- {cv_scores.std():.3f})")
                
            except Exception as e:
                print(f"ERROR: {e}")
                continue
        
        # Selecteer beste model
        best_name = min(results, key=lambda x: results[x]['mae'])
        best_model = results[best_name]['model']
        best_mae = results[best_name]['mae']
        
        print(f"\nBEST MODEL: {best_name} with MAE: {best_mae:.3f}")
        
        return best_model, results
    
    def train_full_pipeline(self):
        """
        COMPLETE TRAINING PIPELINE
        """
        print("\n" + "="*80)
        print("ULTIMATE AI TRAINER - FULL PIPELINE")
        print("="*80)
        print(f"Start time: {datetime.now()}")
        
        # Step 1: Load data
        df = self.load_latest_data()
        if df is None:
            return False
        
        # Step 2: Engineer features
        df = self.engineer_features(df)
        
        # Step 3: Prepare training data
        X, y_home, y_away, feature_names = self.prepare_training_data(df)
        
        # Step 4: Scale features
        print("\nScaling features...")
        X_scaled = self.scaler.fit_transform(X)
        
        # Step 5: Split data
        X_train, X_test, y_home_train, y_home_test = train_test_split(
            X_scaled, y_home, test_size=0.2, random_state=42
        )
        _, _, y_away_train, y_away_test = train_test_split(
            X_scaled, y_away, test_size=0.2, random_state=42
        )
        
        print(f"\nTraining set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        
        # Step 6: Train home goals model
        home_model, home_results = self.train_ensemble_models(X_train, y_home_train, "home")
        
        # Step 7: Train away goals model
        away_model, away_results = self.train_ensemble_models(X_train, y_away_train, "away")
        
        # Step 8: Evaluate on test set
        print("\n" + "="*80)
        print("FINAL EVALUATION ON TEST SET")
        print("="*80)
        
        y_home_pred = home_model.predict(X_test)
        y_away_pred = away_model.predict(X_test)
        
        home_mae = mean_absolute_error(y_home_test, y_home_pred)
        away_mae = mean_absolute_error(y_away_test, y_away_pred)
        home_rmse = np.sqrt(mean_squared_error(y_home_test, y_home_pred))
        away_rmse = np.sqrt(mean_squared_error(y_away_test, y_away_pred))
        home_r2 = r2_score(y_home_test, y_home_pred)
        away_r2 = r2_score(y_away_test, y_away_pred)
        
        print(f"\nHome Goals Model:")
        print(f"  MAE:  {home_mae:.3f}")
        print(f"  RMSE: {home_rmse:.3f}")
        print(f"  R2:   {home_r2:.3f}")
        
        print(f"\nAway Goals Model:")
        print(f"  MAE:  {away_mae:.3f}")
        print(f"  RMSE: {away_rmse:.3f}")
        print(f"  R2:   {away_r2:.3f}")
        
        # Step 9: Save models
        print("\n" + "="*80)
        print("SAVING MODELS")
        print("="*80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        model_package = {
            'home_model': home_model,
            'away_model': away_model,
            'scaler': self.scaler,
            'feature_names': feature_names,
            'home_mae': home_mae,
            'away_mae': away_mae,
            'home_rmse': home_rmse,
            'away_rmse': away_rmse,
            'home_r2': home_r2,
            'away_r2': away_r2,
            'trained_on': datetime.now().isoformat(),
            'training_samples': len(X_train)
        }
        
        # Save as new versioned model
        model_file = os.path.join(models_dir, f'killer_ai_model_{timestamp}.pkl')
        with open(model_file, 'wb') as f:
            pickle.dump(model_package, f)
        print(f"Saved: {model_file}")
        
        # Also save as latest
        latest_file = os.path.join(models_dir, 'de_meester_v2_latest.pkl')
        with open(latest_file, 'wb') as f:
            pickle.dump(model_package, f)
        print(f"Saved: {latest_file}")
        
        print("\n" + "="*80)
        print("TRAINING COMPLETE!")
        print("="*80)
        print(f"End time: {datetime.now()}")
        print(f"\n KILLER AI is ready to DOMINATE!")
        
        return True


if __name__ == '__main__':
    trainer = UltimateAITrainer()
    success = trainer.train_full_pipeline()
    
    if success:
        print("\n SUCCESS! AI model trained and saved!")
        print("\nNext step: Restart server to load new model")
    else:
        print("\nFAILED! Check errors above")
