"""
🎯 ADVANCED SCORE PREDICTOR
Getraind op EXACTE scores - niet alleen winner prediction

Models:
1. Home Score Classifier (0-5 goals)
2. Away Score Classifier (0-5 goals)
3. Exact Score Probabilities
4. Ensemble predictor

Features:
- Team strength (odds)
- Historical score patterns
- Home advantage
- League context
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
import pickle
from datetime import datetime
import os

class AdvancedScorePredictor:
    """Predict EXACT scores"""
    
    def __init__(self):
        self.home_score_model = None
        self.away_score_model = None
        self.exact_score_model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def load_training_data(self):
        """Load training dataset"""
        print("\n" + "="*80)
        print("[LOAD] Loading training data...")
        print("="*80)
        
        # Find latest training dataset (prefer expanded datasets)
        import glob
        
        # Try expanded datasets first
        files = glob.glob('data/training_dataset_expanded_*.csv')
        
        if not files:
            # Fall back to regular datasets
            files = glob.glob('data/training_dataset_*.csv')
        
        if not files:
            print("[ERROR] No training data found!")
            print("[INFO] Run: python scripts/ultimate_training_collector.py")
            return None
        
        latest_file = max(files, key=os.path.getctime)
        print(f"[LOAD] File: {latest_file}")
        
        df = pd.read_csv(latest_file)
        print(f"[LOAD] Loaded {len(df)} matches")
        
        return df
    
    def engineer_features(self, df):
        """Create features for score prediction"""
        print("\n" + "="*80)
        print("[FEATURES] Engineering features...")
        print("="*80)
        
        # Ensure numeric types
        df['home_score'] = df['home_score'].astype(int)
        df['away_score'] = df['away_score'].astype(int)
        
        # Feature 1: Odds-based strength
        if 'home_odds' in df.columns and 'away_odds' in df.columns:
            df['odds_ratio'] = df['home_odds'] / df['away_odds']
            df['home_strength'] = 1 / df['home_odds']  # Lower odds = stronger team
            df['away_strength'] = 1 / df['away_odds']
            df['match_competitiveness'] = abs(df['home_odds'] - df['away_odds'])
        else:
            # Default values if odds not available
            df['odds_ratio'] = 1.0
            df['home_strength'] = 0.5
            df['away_strength'] = 0.5
            df['match_competitiveness'] = 0.0
        
        # Feature 2: Expected goals proxy (from odds)
        df['expected_home_goals'] = df['home_strength'] * 1.5  # Home advantage
        df['expected_away_goals'] = df['away_strength'] * 1.2
        
        # Feature 3: League encoding
        if 'league' in df.columns:
            le_league = LabelEncoder()
            df['league_encoded'] = le_league.fit_transform(df['league'])
            self.label_encoders['league'] = le_league
        else:
            df['league_encoded'] = 0
        
        # Feature 4: Total goals category (affects score distribution)
        df['total_goals'] = df['home_score'] + df['away_score']
        df['goal_difference'] = df['home_score'] - df['away_score']
        
        # Feature 5: Score patterns
        df['is_draw'] = (df['home_score'] == df['away_score']).astype(int)
        df['is_home_win'] = (df['home_score'] > df['away_score']).astype(int)
        df['is_high_scoring'] = (df['total_goals'] >= 4).astype(int)
        df['is_low_scoring'] = (df['total_goals'] <= 1).astype(int)
        
        # Feature columns
        feature_cols = [
            'odds_ratio', 'home_strength', 'away_strength', 'match_competitiveness',
            'expected_home_goals', 'expected_away_goals', 'league_encoded'
        ]
        
        print(f"[FEATURES] Created {len(feature_cols)} features")
        print(f"[FEATURES] Feature list: {feature_cols}")
        
        return df, feature_cols
    
    def train_models(self, df, feature_cols):
        """Train score prediction models"""
        print("\n" + "="*80)
        print("[TRAIN] Training models...")
        print("="*80)
        
        # Prepare data
        X = df[feature_cols]
        y_home = df['home_score'].clip(0, 5)  # Cap at 5 goals
        y_away = df['away_score'].clip(0, 5)
        
        # Create exact score labels (e.g., "1-0", "2-1")
        y_exact = df['home_score'].astype(str) + '-' + df['away_score'].astype(str)
        
        # Split data
        X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test, y_exact_train, y_exact_test = train_test_split(
            X, y_home, y_away, y_exact,
            test_size=0.2,
            random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"\n[TRAIN] Training set: {len(X_train)} matches")
        print(f"[TRAIN] Test set: {len(X_test)} matches")
        
        # Model 1: Home Score Classifier
        print("\n[TRAIN] Training Home Score Model...")
        self.home_score_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.home_score_model.fit(X_train_scaled, y_home_train)
        
        home_pred = self.home_score_model.predict(X_test_scaled)
        home_acc = accuracy_score(y_home_test, home_pred)
        print(f"[TRAIN] Home Score Accuracy: {home_acc:.3f}")
        
        # Model 2: Away Score Classifier
        print("\n[TRAIN] Training Away Score Model...")
        self.away_score_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.away_score_model.fit(X_train_scaled, y_away_train)
        
        away_pred = self.away_score_model.predict(X_test_scaled)
        away_acc = accuracy_score(y_away_test, away_pred)
        print(f"[TRAIN] Away Score Accuracy: {away_acc:.3f}")
        
        # Model 3: Exact Score (top 15 most common scores)
        print("\n[TRAIN] Training Exact Score Model...")
        
        # Only train on most common scores (realistic to predict)
        score_counts = y_exact_train.value_counts()
        top_scores = score_counts.head(15).index.tolist()
        
        # Filter training data to common scores
        mask_train = y_exact_train.isin(top_scores)
        mask_test = y_exact_test.isin(top_scores)
        
        if mask_train.sum() > 50:  # Need enough samples
            self.exact_score_model = RandomForestClassifier(
                n_estimators=300,
                max_depth=8,
                random_state=42
            )
            self.exact_score_model.fit(
                X_train_scaled[mask_train],
                y_exact_train[mask_train]
            )
            
            if mask_test.sum() > 0:
                exact_pred = self.exact_score_model.predict(X_test_scaled[mask_test])
                exact_acc = accuracy_score(y_exact_test[mask_test], exact_pred)
                print(f"[TRAIN] Exact Score Accuracy (top 15): {exact_acc:.3f}")
        
        # Combined accuracy
        combined_pred = [f"{h}-{a}" for h, a in zip(home_pred, away_pred)]
        combined_exact = [f"{h}-{a}" for h, a in zip(y_home_test, y_away_test)]
        combined_acc = accuracy_score(combined_exact, combined_pred)
        
        print(f"\n[TRAIN] Combined Model Accuracy: {combined_acc:.3f}")
        
        # Show confusion matrix for home goals
        print("\n[TRAIN] Home Goals Confusion Matrix:")
        cm = confusion_matrix(y_home_test, home_pred)
        print(cm)
        
        # Save feature importance
        print("\n[TRAIN] Top 5 Important Features:")
        importances = self.home_score_model.feature_importances_
        for i, imp in sorted(enumerate(importances), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {feature_cols[i]}: {imp:.3f}")
        
        return {
            'home_accuracy': home_acc,
            'away_accuracy': away_acc,
            'combined_accuracy': combined_acc,
            'exact_accuracy': exact_acc if self.exact_score_model else 0.0
        }
    
    def save_model(self):
        """Save trained models"""
        print("\n" + "="*80)
        print("[SAVE] Saving models...")
        print("="*80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        model_data = {
            'home_score_model': self.home_score_model,
            'away_score_model': self.away_score_model,
            'exact_score_model': self.exact_score_model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'version': 'advanced_v1.0',
            'trained_at': timestamp
        }
        
        # Save to main model file
        model_file = 'data/score_predictor.pkl'
        with open(model_file, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"[SAVE] Main model: {model_file}")
        
        # Save versioned backup
        backup_file = f'data/score_predictor_{timestamp}.pkl'
        with open(backup_file, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"[SAVE] Backup: {backup_file}")
    
    def run_training(self):
        """Complete training pipeline"""
        print("\n" + "="*80)
        print("🎯 ADVANCED SCORE PREDICTOR TRAINING")
        print("="*80)
        print(f"Start: {datetime.now()}\n")
        
        # Load data
        df = self.load_training_data()
        if df is None:
            return
        
        # Engineer features
        df, feature_cols = self.engineer_features(df)
        
        # Train models
        metrics = self.train_models(df, feature_cols)
        
        # Save models
        self.save_model()
        
        # Final report
        print("\n" + "="*80)
        print("✅ TRAINING COMPLETE")
        print("="*80)
        print("\nModel Performance:")
        print(f"  Home Score Accuracy:  {metrics['home_accuracy']:.1%}")
        print(f"  Away Score Accuracy:  {metrics['away_accuracy']:.1%}")
        print(f"  Combined Accuracy:    {metrics['combined_accuracy']:.1%}")
        print(f"  Exact Score Accuracy: {metrics['exact_accuracy']:.1%}")
        
        print("\nModel saved to: data/score_predictor.pkl")
        print("\n🎯 Ready to predict EXACT scores!")


def main():
    predictor = AdvancedScorePredictor()
    predictor.run_training()


if __name__ == '__main__':
    main()
