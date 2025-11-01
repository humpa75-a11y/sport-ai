"""
🚀 QUICK PREDICTION TOOL
Predict scores direct vanaf command line of import in andere scripts
"""

import sys
import pickle
import pandas as pd
import numpy as np
from datetime import datetime


def quick_predict(home_team, away_team, home_odds, away_odds, draw_odds, league='Eredivisie'):
    """Quick score prediction - 1 functie voor alles"""
    
    # Load model
    try:
        with open('data/score_predictor.pkl', 'rb') as f:
            model_data = pickle.load(f)
    except FileNotFoundError:
        print("❌ ERROR: Model not found! Run: python scripts/train_score_predictor.py")
        return None
    
    # Prepare features
    odds_ratio = home_odds / away_odds
    home_strength = 1 / home_odds
    away_strength = 1 / away_odds
    match_competitiveness = abs(home_odds - away_odds)
    expected_home_goals = home_strength * 1.5
    expected_away_goals = away_strength * 1.2
    
    # Encode league
    le_league = model_data['label_encoders'].get('league')
    if le_league and league in le_league.classes_:
        league_encoded = le_league.transform([league])[0]
    else:
        league_encoded = 0
    
    # Create features
    features = np.array([[
        odds_ratio, home_strength, away_strength, match_competitiveness,
        expected_home_goals, expected_away_goals, league_encoded
    ]])
    
    # Scale
    features_scaled = model_data['scaler'].transform(features)
    
    # Predict
    home_model = model_data['home_score_model']
    away_model = model_data['away_score_model']
    
    home_probs = home_model.predict_proba(features_scaled)[0]
    away_probs = away_model.predict_proba(features_scaled)[0]
    
    home_pred = home_model.predict(features_scaled)[0]
    away_pred = away_model.predict(features_scaled)[0]
    
    # Top scores
    score_probs = []
    for h in range(len(home_probs)):
        for a in range(len(away_probs)):
            prob = home_probs[h] * away_probs[a]
            score_probs.append((f"{h}-{a}", prob))
    
    score_probs.sort(key=lambda x: x[1], reverse=True)
    
    return {
        'home_team': home_team,
        'away_team': away_team,
        'predicted_score': f"{home_pred}-{away_pred}",
        'home_goals': int(home_pred),
        'away_goals': int(away_pred),
        'confidence': float(home_probs[home_pred] * away_probs[away_pred]),
        'top_5_scores': score_probs[:5],
        'home_probs': {i: float(p) for i, p in enumerate(home_probs)},
        'away_probs': {i: float(p) for i, p in enumerate(away_probs)}
    }


def print_prediction(result):
    """Pretty print prediction results"""
    if not result:
        return
    
    print("\n" + "="*70)
    print(f"🎯 {result['home_team']} vs {result['away_team']}")
    print("="*70)
    print(f"\n🔮 PREDICTION: {result['predicted_score']}")
    print(f"   Confidence: {result['confidence']:.1%}\n")
    
    print("📊 Top 5 Most Likely Scores:")
    for i, (score, prob) in enumerate(result['top_5_scores'], 1):
        bar = "█" * int(prob * 50)
        print(f"   {i}. {score:5s} {prob:6.1%} {bar}")
    
    print("\n" + "="*70)


def calculate_value_bet(predicted_prob, bookmaker_odds, min_edge=0.10):
    """Calculate betting value"""
    implied_prob = 1 / bookmaker_odds
    value = (predicted_prob * bookmaker_odds) - 1
    
    return {
        'value': value,
        'edge': value,
        'predicted_prob': predicted_prob,
        'implied_prob': implied_prob,
        'recommendation': 'BET!' if value > min_edge else 'SKIP'
    }


def analyze_value_bets(result, score_odds):
    """
    Analyze value bets for multiple scores
    
    score_odds = {
        '1-0': 7.50,
        '2-1': 9.00,
        '1-1': 6.50,
        # etc.
    }
    """
    
    print("\n" + "="*70)
    print("💰 VALUE BET ANALYSIS")
    print("="*70)
    
    value_bets = []
    
    for score, odds in score_odds.items():
        # Find predicted probability
        pred_prob = 0.0
        for pred_score, prob in result['top_5_scores']:
            if pred_score == score:
                pred_prob = prob
                break
        
        if pred_prob > 0:
            value_analysis = calculate_value_bet(pred_prob, odds)
            
            if value_analysis['value'] > 0:
                value_bets.append({
                    'score': score,
                    'odds': odds,
                    **value_analysis
                })
                
                print(f"\n🎯 Score {score} @ {odds}")
                print(f"   Model probability:     {value_analysis['predicted_prob']:.1%}")
                print(f"   Bookmaker probability: {value_analysis['implied_prob']:.1%}")
                print(f"   Value:                 {value_analysis['value']:.1%}")
                print(f"   Recommendation:        {value_analysis['recommendation']}")
    
    if not value_bets:
        print("\n⚠️  No value bets found with current odds")
    
    print("="*70)
    
    return value_bets


# Command line interface
if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        # Demo mode
        print("\n🎯 QUICK PREDICTION DEMO\n")
        
        result = quick_predict(
            home_team='Ajax',
            away_team='PSV',
            home_odds=2.10,
            away_odds=3.20,
            draw_odds=3.40,
            league='Eredivisie'
        )
        
        print_prediction(result)
        
        # Example value bet analysis
        example_odds = {
            '1-0': 7.50,
            '2-0': 9.00,
            '2-1': 8.50,
            '1-1': 6.00,
            '0-0': 11.00
        }
        
        analyze_value_bets(result, example_odds)
        
        print("\n📖 USAGE:")
        print("   python scripts/quick_predict.py Ajax PSV 2.10 3.20 3.40")
        print("   python scripts/quick_predict.py \"Manchester City\" Liverpool 1.95 3.60 3.80 \"Premier League\"")
        print()
        
    elif len(sys.argv) >= 6:
        # Command line mode
        home_team = sys.argv[1]
        away_team = sys.argv[2]
        home_odds = float(sys.argv[3])
        away_odds = float(sys.argv[4])
        draw_odds = float(sys.argv[5])
        league = sys.argv[6] if len(sys.argv) > 6 else 'Eredivisie'
        
        result = quick_predict(home_team, away_team, home_odds, away_odds, draw_odds, league)
        print_prediction(result)
    
    else:
        print("\n❌ USAGE:")
        print("   python scripts/quick_predict.py HOME AWAY HOME_ODDS AWAY_ODDS DRAW_ODDS [LEAGUE]")
        print("\nExample:")
        print('   python scripts/quick_predict.py Ajax PSV 2.10 3.20 3.40 Eredivisie')
        print()
