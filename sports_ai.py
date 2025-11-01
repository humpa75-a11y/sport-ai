"""
🤖 SPORTS AI - COMPLETE PREDICTION SYSTEM 🤖

Dit systeem:
1. Laadt data van de KillerMachine
2. Preprocessed de data (cleaning + feature engineering)
3. Traint een ML model
4. Voorspelt wedstrijduitslagen met odds
5. Vindt value bets (waar je kan winnen!)

GEBRUIK:
1. Run eerst killermachine.py om data te verzamelen
2. Run dan dit bestand: python sports_ai.py
3. Krijg predictions met winkansen!
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
import glob
import warnings
warnings.filterwarnings('ignore')

# Machine Learning
try:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, classification_report
    import pickle
except ImportError:
    print("❌ sklearn not installed! Run: pip install scikit-learn")
    exit()

class SportsAI:
    """🤖 De AI die wedstrijden voorspelt"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        self.data = {}
        
        print("="*80)
        print("🤖 SPORTS AI INITIALIZED")
        print("="*80 + "\n")
    
    # ==================== DATA LOADING ====================
    
    def load_killermachine_data(self):
        """📁 Laad alle data van KillerMachine"""
        print("📁 Loading KillerMachine data...\n")
        
        # Zoek de nieuwste bestanden
        files = {
            'fixtures': glob.glob('fixtures_*.csv'),
            'odds': glob.glob('odds_*.csv'),
            'standings': glob.glob('standings_*.csv'),
            'team_stats': glob.glob('team_stats_*.csv'),
            'injuries': glob.glob('injuries_*.csv')
        }
        
        # Laad elk bestand (nieuwste versie)
        for key, file_list in files.items():
            if file_list:
                latest_file = sorted(file_list)[-1]
                try:
                    self.data[key] = pd.read_csv(latest_file)
                    print(f"✅ {key:<15}: {len(self.data[key]):>6,} rows from {latest_file}")
                except Exception as e:
                    print(f"⚠️  {key}: Error - {str(e)}")
                    self.data[key] = pd.DataFrame()
            else:
                print(f"❌ {key}: No files found")
                self.data[key] = pd.DataFrame()
        
        print(f"\n📊 Total data points: {sum(len(df) for df in self.data.values()):,}")
        return self.data
    
    # ==================== DATA PREPROCESSING ====================
    
    def preprocess_data(self):
        """🔧 Maak data klaar voor AI"""
        print("\n" + "="*80)
        print("🔧 PREPROCESSING DATA FOR AI")
        print("="*80 + "\n")
        
        if self.data['fixtures'].empty:
            print("❌ No fixtures data available!")
            return None
        
        # Start met fixtures als basis
        df = self.data['fixtures'].copy()
        
        print(f"📊 Starting with {len(df)} fixtures")
        
        # Filter alleen afgeronde wedstrijden (voor training)
        df_finished = df[df['status'].str.contains('Finished|Match Finished|FT', case=False, na=False)].copy()
        print(f"✅ Finished matches: {len(df_finished)}")
        
        if len(df_finished) < 50:
            print("⚠️  Warning: Weinig afgeronde wedstrijden voor training!")
            print("    Run killermachine.py eerst om meer data te verzamelen!")
        
        # Maak target variabele (uitslag)
        df_finished['result'] = df_finished.apply(self._determine_result, axis=1)
        
        # Feature Engineering
        print("\n🔨 Creating features...")
        
        # 1. Add odds data
        if not self.data['odds'].empty:
            df_finished = self._add_odds_features(df_finished)
            print("   ✅ Odds features added")
        
        # 2. Add team stats
        if not self.data['team_stats'].empty:
            df_finished = self._add_team_stats_features(df_finished)
            print("   ✅ Team stats features added")
        
        # 3. Add standings
        if not self.data['standings'].empty:
            df_finished = self._add_standings_features(df_finished)
            print("   ✅ Standings features added")
        
        # 4. Add injuries impact
        if not self.data['injuries'].empty:
            df_finished = self._add_injury_features(df_finished)
            print("   ✅ Injury features added")
        
        # Drop rows met missing target
        df_finished = df_finished.dropna(subset=['result'])
        
        print(f"\n📊 Final dataset: {len(df_finished)} matches")
        print(f"📊 Features: {len([col for col in df_finished.columns if col.startswith('feat_')])}")
        
        return df_finished
    
    def _determine_result(self, row):
        """Bepaal uitslag: Home Win (H), Draw (D), Away Win (A)"""
        try:
            home_goals = float(row['home_goals'])
            away_goals = float(row['away_goals'])
            
            if pd.isna(home_goals) or pd.isna(away_goals):
                return None
            
            if home_goals > away_goals:
                return 'H'
            elif home_goals < away_goals:
                return 'A'
            else:
                return 'D'
        except:
            return None
    
    def _add_odds_features(self, df):
        """Voeg odds features toe"""
        if self.data['odds'].empty:
            return df
        
        odds_df = self.data['odds'].copy()
        
        # Gemiddelde odds per wedstrijd
        odds_agg = odds_df.groupby(['home_team', 'away_team']).agg({
            'odds_home': 'mean',
            'odds_draw': 'mean',
            'odds_away': 'mean'
        }).reset_index()
        
        # Merge met fixtures
        df = df.merge(odds_agg, on=['home_team', 'away_team'], how='left', suffixes=('', '_odds'))
        
        # Rename naar features
        df['feat_odds_home'] = pd.to_numeric(df['odds_home'], errors='coerce').fillna(2.0)
        df['feat_odds_draw'] = pd.to_numeric(df['odds_draw'], errors='coerce').fillna(3.5)
        df['feat_odds_away'] = pd.to_numeric(df['odds_away'], errors='coerce').fillna(3.0)
        
        # Implied probabilities
        df['feat_prob_home'] = 1 / df['feat_odds_home']
        df['feat_prob_draw'] = 1 / df['feat_odds_draw']
        df['feat_prob_away'] = 1 / df['feat_odds_away']
        
        return df
    
    def _add_team_stats_features(self, df):
        """Voeg team statistieken toe"""
        if self.data['team_stats'].empty:
            return df
        
        stats = self.data['team_stats'].copy()
        
        # Home team stats
        df = df.merge(
            stats[['team_name', 'goals_for', 'goals_against']],
            left_on='home_team', right_on='team_name', how='left', suffixes=('', '_home')
        )
        
        df['feat_home_goals_for'] = pd.to_numeric(df['goals_for'], errors='coerce').fillna(0)
        df['feat_home_goals_against'] = pd.to_numeric(df['goals_against'], errors='coerce').fillna(0)
        
        # Away team stats
        df = df.merge(
            stats[['team_name', 'goals_for', 'goals_against']],
            left_on='away_team', right_on='team_name', how='left', suffixes=('_home', '_away')
        )
        
        df['feat_away_goals_for'] = pd.to_numeric(df['goals_for_away'], errors='coerce').fillna(0)
        df['feat_away_goals_against'] = pd.to_numeric(df['goals_against_away'], errors='coerce').fillna(0)
        
        return df
    
    def _add_standings_features(self, df):
        """Voeg competitie positie toe"""
        if self.data['standings'].empty:
            return df
        
        standings = self.data['standings'].copy()
        
        # Home team positie
        df = df.merge(
            standings[['team_name', 'rank', 'points']],
            left_on='home_team', right_on='team_name', how='left', suffixes=('', '_home')
        )
        
        df['feat_home_position'] = pd.to_numeric(df['rank'], errors='coerce').fillna(10)
        df['feat_home_points'] = pd.to_numeric(df['points'], errors='coerce').fillna(0)
        
        # Away team positie
        df = df.merge(
            standings[['team_name', 'rank', 'points']],
            left_on='away_team', right_on='team_name', how='left', suffixes=('_home', '_away')
        )
        
        df['feat_away_position'] = pd.to_numeric(df['rank_away'], errors='coerce').fillna(10)
        df['feat_away_points'] = pd.to_numeric(df['points_away'], errors='coerce').fillna(0)
        
        # Position difference
        df['feat_position_diff'] = df['feat_away_position'] - df['feat_home_position']
        
        return df
    
    def _add_injury_features(self, df):
        """Voeg blessure impact toe"""
        if self.data['injuries'].empty:
            return df
        
        injuries = self.data['injuries'].copy()
        
        # Tel blessures per team
        injury_count = injuries.groupby('team_name').size().reset_index(name='injury_count')
        
        # Home team injuries
        df = df.merge(injury_count, left_on='home_team', right_on='team_name', how='left')
        df['feat_home_injuries'] = df['injury_count'].fillna(0)
        
        # Away team injuries
        df = df.merge(injury_count, left_on='away_team', right_on='team_name', how='left', suffixes=('', '_away'))
        df['feat_away_injuries'] = df['injury_count_away'].fillna(0)
        
        return df
    
    # ==================== MODEL TRAINING ====================
    
    def train_model(self, df):
        """🎓 Train het AI model"""
        print("\n" + "="*80)
        print("🎓 TRAINING AI MODEL")
        print("="*80 + "\n")
        
        # Selecteer feature columns
        feature_cols = [col for col in df.columns if col.startswith('feat_')]
        
        if len(feature_cols) == 0:
            print("❌ No features found! Cannot train model.")
            return None
        
        print(f"📊 Training with {len(feature_cols)} features:")
        for feat in feature_cols[:10]:
            print(f"   - {feat}")
        if len(feature_cols) > 10:
            print(f"   ... and {len(feature_cols) - 10} more")
        
        # Prepare data
        X = df[feature_cols].fillna(0)
        y = df['result']
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42
        )
        
        print(f"\n📊 Training set: {len(X_train)} matches")
        print(f"📊 Test set: {len(X_test)} matches")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print("\n🤖 Training Random Forest...")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ Model trained!")
        print(f"📊 Accuracy: {accuracy*100:.2f}%")
        
        self.feature_columns = feature_cols
        
        # Save model
        self._save_model()
        
        return self.model
    
    def _save_model(self):
        """💾 Sla model op"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_columns': self.feature_columns,
            'timestamp': timestamp
        }
        
        filename = f"sports_ai_model_{timestamp}.pkl"
        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"\n💾 Model saved: {filename}")
    
    # ==================== PREDICTIONS ====================
    
    def predict_upcoming_matches(self):
        """🔮 Voorspel aankomende wedstrijden"""
        print("\n" + "="*80)
        print("🔮 PREDICTING UPCOMING MATCHES")
        print("="*80 + "\n")
        
        if self.model is None:
            print("❌ No model trained! Run train_model() first.")
            return None
        
        # Haal upcoming fixtures op
        df = self.data['fixtures'].copy()
        df_upcoming = df[df['status'].str.contains('Not Started|NS|Scheduled', case=False, na=False)].copy()
        
        if df_upcoming.empty:
            print("ℹ️  No upcoming matches found in data")
            return None
        
        print(f"📊 Found {len(df_upcoming)} upcoming matches")
        
        # Add features
        if not self.data['odds'].empty:
            df_upcoming = self._add_odds_features(df_upcoming)
        if not self.data['team_stats'].empty:
            df_upcoming = self._add_team_stats_features(df_upcoming)
        if not self.data['standings'].empty:
            df_upcoming = self._add_standings_features(df_upcoming)
        if not self.data['injuries'].empty:
            df_upcoming = self._add_injury_features(df_upcoming)
        
        # Prepare features
        X_pred = df_upcoming[self.feature_columns].fillna(0)
        X_pred_scaled = self.scaler.transform(X_pred)
        
        # Predict
        predictions = self.model.predict(X_pred_scaled)
        probabilities = self.model.predict_proba(X_pred_scaled)
        
        # Create results dataframe
        results = df_upcoming[['home_team', 'away_team', 'date']].copy()
        
        if 'feat_odds_home' in df_upcoming.columns:
            results['odds_home'] = df_upcoming['feat_odds_home']
            results['odds_draw'] = df_upcoming['feat_odds_draw']
            results['odds_away'] = df_upcoming['feat_odds_away']
        
        results['prediction'] = self.label_encoder.inverse_transform(predictions)
        
        # Add probabilities
        for idx, label in enumerate(self.label_encoder.classes_):
            results[f'prob_{label}'] = probabilities[:, idx]
        
        # Sort by confidence
        results['confidence'] = results[[f'prob_{label}' for label in self.label_encoder.classes_]].max(axis=1)
        results = results.sort_values('confidence', ascending=False)
        
        print(f"\n🎯 TOP 10 PREDICTIONS:")
        print("="*80)
        
        for idx, row in results.head(10).iterrows():
            print(f"\n{row['home_team']} vs {row['away_team']}")
            print(f"   Date: {row['date']}")
            print(f"   Prediction: {row['prediction']} (Confidence: {row['confidence']*100:.1f}%)")
            
            probs_str = " ".join([f"{label}={row[f'prob_{label}']*100:.1f}%" 
                                 for label in self.label_encoder.classes_])
            print(f"   Probabilities: {probs_str}")
        
        # Save predictions
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"predictions_{timestamp}.csv"
        results.to_csv(filename, index=False)
        print(f"\n💾 Predictions saved: {filename}")
        
        return results

# ==================== MAIN ====================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║              🤖 SPORTS AI - PREDICTION SYSTEM 🤖                ║
    ║                                                                  ║
    ║                  MASTERCLASS AI VOOR VOETBAL                     ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize AI
    ai = SportsAI()
    
    # 1. Load data
    ai.load_killermachine_data()
    
    # 2. Preprocess
    df_processed = ai.preprocess_data()
    
    if df_processed is not None and len(df_processed) > 50:
        # 3. Train model
        ai.train_model(df_processed)
        
        # 4. Make predictions
        predictions = ai.predict_upcoming_matches()
        
        print("""
        ╔══════════════════════════════════════════════════════════════════╗
        ║                                                                  ║
        ║                     🎉 AI KLAAR! 🎉                             ║
        ║                                                                  ║
        ║   Je hebt nu:                                                    ║
        ║   ✅ Getraind AI model                                          ║
        ║   ✅ Predictions voor aankomende wedstrijden                    ║
        ║   ✅ Model opgeslagen voor later gebruik                        ║
        ║                                                                  ║
        ║   📁 Check: predictions_[timestamp].csv                         ║
        ║   📁 Check: sports_ai_model_[timestamp].pkl                     ║
        ║                                                                  ║
        ╚══════════════════════════════════════════════════════════════════╝
        """)
    else:
        print("\n❌ Not enough data to train model!")
        print("   You need at least 50 finished matches.")
        print("   Run killermachine.py first to collect data!")