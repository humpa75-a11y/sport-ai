"""
🔮 SCORE PREDICTION ENGINE
Load trained model and predict EXACT scores for upcoming matches
"""

import pickle
import pandas as pd
import numpy as np
from datetime import datetime

class ScorePredictor:
    """Predict exact scores using trained model"""
    
    def __init__(self):
        self.model_data = None
        self.load_model()
    
    def load_model(self):
        """Load trained model"""
        try:
            with open('data/score_predictor.pkl', 'rb') as f:
                self.model_data = pickle.load(f)
            
            print("\n" + "="*80)
            print("✅ MODEL LOADED")
            print("="*80)
            print(f"Version: {self.model_data.get('version', 'unknown')}")
            print(f"Trained: {self.model_data.get('trained_at', 'unknown')}")
            print("="*80 + "\n")
            
        except FileNotFoundError:
            print("\n❌ ERROR: Model not found!")
            print("Run first: python scripts/train_score_predictor.py\n")
            exit(1)
    
    def prepare_features(self, home_odds, away_odds, draw_odds, league='Eredivisie'):
        """Prepare features for prediction"""
        
        # Calculate features (same as training)
        odds_ratio = home_odds / away_odds
        home_strength = 1 / home_odds
        away_strength = 1 / away_odds
        match_competitiveness = abs(home_odds - away_odds)
        expected_home_goals = home_strength * 1.5
        expected_away_goals = away_strength * 1.2
        
        # Encode league
        le_league = self.model_data['label_encoders'].get('league')
        if le_league and league in le_league.classes_:
            league_encoded = le_league.transform([league])[0]
        else:
            league_encoded = 0
        
        # Create feature array
        features = np.array([[
            odds_ratio,
            home_strength,
            away_strength,
            match_competitiveness,
            expected_home_goals,
            expected_away_goals,
            league_encoded
        ]])
        
        # Scale features
        features_scaled = self.model_data['scaler'].transform(features)
        
        return features_scaled
    
    def predict_score(self, home_team, away_team, home_odds, away_odds, draw_odds, league='Eredivisie'):
        """Predict exact score with probabilities"""
        
        print("\n" + "="*80)
        print(f"🎯 PREDICTING: {home_team} vs {away_team}")
        print("="*80)
        print(f"League: {league}")
        print(f"Odds: {home_odds:.2f} - {draw_odds:.2f} - {away_odds:.2f}")
        print("-"*80)
        
        # Prepare features
        features = self.prepare_features(home_odds, away_odds, draw_odds, league)
        
        # Get models
        home_model = self.model_data['home_score_model']
        away_model = self.model_data['away_score_model']
        exact_model = self.model_data.get('exact_score_model')
        
        # Predict home goals (with probabilities)
        home_probs = home_model.predict_proba(features)[0]
        home_pred = home_model.predict(features)[0]
        
        # Predict away goals (with probabilities)
        away_probs = away_model.predict_proba(features)[0]
        away_pred = away_model.predict(features)[0]
        
        # Most likely score
        predicted_score = f"{home_pred}-{away_pred}"
        
        print("\n📊 PREDICTION RESULTS:")
        print("="*80)
        print(f"Most Likely Score: {predicted_score}")
        print(f"Home Goals: {home_pred} (confidence: {home_probs[home_pred]:.1%})")
        print(f"Away Goals: {away_pred} (confidence: {away_probs[away_pred]:.1%})")
        
        # Show home goal probabilities
        print("\n🏠 Home Goals Distribution:")
        for i, prob in enumerate(home_probs):
            bar = "█" * int(prob * 50)
            print(f"  {i} goals: {prob:6.1%} {bar}")
        
        # Show away goal probabilities
        print("\n✈️  Away Goals Distribution:")
        for i, prob in enumerate(away_probs):
            bar = "█" * int(prob * 50)
            print(f"  {i} goals: {prob:6.1%} {bar}")
        
        # Top 5 most likely exact scores
        print("\n🎯 Top 5 Most Likely Exact Scores:")
        score_probs = []
        for h in range(len(home_probs)):
            for a in range(len(away_probs)):
                prob = home_probs[h] * away_probs[a]  # Independent probability
                score_probs.append((f"{h}-{a}", prob))
        
        score_probs.sort(key=lambda x: x[1], reverse=True)
        
        for i, (score, prob) in enumerate(score_probs[:5], 1):
            bar = "█" * int(prob * 100)
            print(f"  {i}. {score}: {prob:6.1%} {bar}")
        
        # If exact score model available
        if exact_model:
            try:
                exact_pred = exact_model.predict(features)[0]
                exact_probs = exact_model.predict_proba(features)[0]
                max_prob_idx = exact_probs.argmax()
                
                print("\n🔮 Exact Score Model Prediction:")
                print(f"  Predicted: {exact_pred}")
                print(f"  Confidence: {exact_probs[max_prob_idx]:.1%}")
            except:
                pass
        
        print("\n" + "="*80)
        
        return {
            'predicted_score': predicted_score,
            'home_goals': int(home_pred),
            'away_goals': int(away_pred),
            'home_confidence': float(home_probs[home_pred]),
            'away_confidence': float(away_probs[away_pred]),
            'top_scores': score_probs[:5]
        }
    
    def predict_multiple(self, matches):
        """Predict scores for multiple matches"""
        results = []
        
        print("\n" + "="*80)
        print("🔮 BATCH PREDICTION")
        print("="*80)
        print(f"Predicting {len(matches)} matches...\n")
        
        for match in matches:
            result = self.predict_score(
                match['home_team'],
                match['away_team'],
                match['home_odds'],
                match['away_odds'],
                match['draw_odds'],
                match.get('league', 'Eredivisie')
            )
            
            result['home_team'] = match['home_team']
            result['away_team'] = match['away_team']
            results.append(result)
        
        return results


def test_predictions():
    """Test with example matches"""
    predictor = ScorePredictor()
    
    # Example matches (use realistic Dutch/English teams and odds)
    test_matches = [
        {
            'home_team': 'Ajax',
            'away_team': 'Feyenoord',
            'home_odds': 1.85,
            'away_odds': 3.80,
            'draw_odds': 3.50,
            'league': 'Eredivisie'
        },
        {
            'home_team': 'PSV',
            'away_team': 'AZ',
            'home_odds': 1.60,
            'away_odds': 5.20,
            'draw_odds': 4.00,
            'league': 'Eredivisie'
        },
        {
            'home_team': 'Manchester City',
            'away_team': 'Liverpool',
            'home_odds': 2.10,
            'away_odds': 3.40,
            'draw_odds': 3.60,
            'league': 'Premier League'
        }
    ]
    
    results = predictor.predict_multiple(test_matches)
    
    # Summary
    print("\n" + "="*80)
    print("📋 PREDICTION SUMMARY")
    print("="*80)
    for r in results:
        print(f"{r['home_team']} vs {r['away_team']}: {r['predicted_score']}")
    print("="*80 + "\n")


if __name__ == '__main__':
    test_predictions()
