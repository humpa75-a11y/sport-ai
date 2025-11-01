"""
🎯 ENSEMBLE PREDICTOR - Multi-Model Predictions

Combine multiple prediction models voor betere accuracy:
1. Poisson Model (current) - xG based
2. ML Model - Team form, H2H, market trends
3. Market Consensus - Average bookmaker odds
4. Historical H2H - Direct matchup history

Weight models by historical accuracy
Output: Ensemble prediction met confidence score

Author: Sport AI Sync
Date: November 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy.stats import poisson
import json
import os
from datetime import datetime


class EnsemblePredictor:
    """
    Combine multiple prediction models
    
    Models:
    1. Poisson (xG-based) - Current implementation
    2. ML Model (form-based) - Team stats + trends
    3. Market Consensus - Bookmaker implied probabilities
    4. H2H Historical - Past meetings
    
    Weights: Based on historical accuracy per model
    """
    
    def __init__(self):
        """Initialize ensemble predictor"""
        self.models = ['poisson', 'ml_form', 'market', 'h2h']
        
        # Default weights (equal until we have historical data)
        self.weights = {
            'poisson': 0.35,      # xG-based (most reliable for goals)
            'ml_form': 0.30,      # Form-based (good for recent trends)
            'market': 0.25,       # Market (smart money)
            'h2h': 0.10          # H2H (least reliable, small sample)
        }
        
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.weights_file = os.path.join(self.data_dir, 'ensemble_weights.json')
        
        self._load_weights()
    
    # ==========================================
    # MODEL 1: POISSON (xG-based)
    # ==========================================
    
    def predict_poisson(self, home_xg: float, away_xg: float, 
                       runs: int = 100) -> Dict:
        """
        Poisson model predictions (current implementation)
        
        Args:
            home_xg: Home team expected goals
            away_xg: Away team expected goals
            runs: Monte Carlo simulations
        
        Returns:
            Dict with probabilities for all markets
        """
        results = {'home_wins': 0, 'draws': 0, 'away_wins': 0, 'scores': []}
        over_under = {1.5: 0, 2.5: 0, 3.5: 0}
        btts_count = 0
        
        for _ in range(runs):
            home_score = np.random.poisson(home_xg)
            away_score = np.random.poisson(away_xg)
            
            results['scores'].append((home_score, away_score))
            
            if home_score > away_score:
                results['home_wins'] += 1
            elif home_score < away_score:
                results['away_wins'] += 1
            else:
                results['draws'] += 1
            
            total_goals = home_score + away_score
            for threshold in over_under:
                if total_goals > threshold:
                    over_under[threshold] += 1
            
            if home_score > 0 and away_score > 0:
                btts_count += 1
        
        return {
            'home_win': results['home_wins'] / runs,
            'draw': results['draws'] / runs,
            'away_win': results['away_wins'] / runs,
            'over_1.5': over_under[1.5] / runs,
            'over_2.5': over_under[2.5] / runs,
            'over_3.5': over_under[3.5] / runs,
            'btts': btts_count / runs
        }
    
    # ==========================================
    # MODEL 2: ML FORM-BASED
    # ==========================================
    
    def predict_ml_form(self, home_form: Dict, away_form: Dict) -> Dict:
        """
        ML model based on team form
        
        Args:
            home_form: {'recent_goals': float, 'recent_conceded': float, 
                       'win_rate': float, 'form_points': float}
            away_form: Same structure
        
        Returns:
            Dict with probabilities
        """
        # Calculate attacking strength
        home_attack = home_form.get('recent_goals', 1.5)
        away_attack = away_form.get('recent_goals', 1.5)
        
        # Calculate defensive strength
        home_defense = home_form.get('recent_conceded', 1.0)
        away_defense = away_form.get('recent_conceded', 1.0)
        
        # Form factor (recent win rate)
        home_form_factor = home_form.get('win_rate', 0.5)
        away_form_factor = away_form.get('win_rate', 0.5)
        
        # Base probabilities (home advantage ~0.55)
        base_home = 0.35 + (home_form_factor * 0.15)
        base_away = 0.25 + (away_form_factor * 0.15)
        base_draw = 0.25  # Fixed draw probability
        
        # Normalize to ensure they sum to 1.0
        total = base_home + base_draw + base_away
        home_win = max(0.1, min(0.7, base_home / total))  # Clamp between 10-70%
        draw = max(0.1, min(0.4, base_draw / total))      # Clamp between 10-40%
        away_win = max(0.1, min(0.7, base_away / total))  # Clamp between 10-70%
        
        # Re-normalize after clamping
        total = home_win + draw + away_win
        home_win = home_win / total
        draw = draw / total
        away_win = away_win / total
        
        # Goals estimates
        expected_home_goals = home_attack * (1 / away_defense) * 1.3  # Home advantage
        expected_away_goals = away_attack * (1 / home_defense)
        
        # Over/Under based on expected goals
        total_expected = expected_home_goals + expected_away_goals
        over_1_5 = min(0.95, total_expected / 2.5)
        over_2_5 = min(0.90, total_expected / 3.5)
        over_3_5 = min(0.85, total_expected / 5.0)
        
        # BTTS (both teams attacking form)
        btts = min(0.85, (home_attack + away_attack) / 4.0)
        
        return {
            'home_win': home_win,
            'draw': draw,
            'away_win': away_win,
            'over_1.5': over_1_5,
            'over_2.5': over_2_5,
            'over_3.5': over_3_5,
            'btts': btts
        }
    
    # ==========================================
    # MODEL 3: MARKET CONSENSUS
    # ==========================================
    
    def predict_market_consensus(self, odds: Dict) -> Dict:
        """
        Market consensus from bookmaker odds
        
        Args:
            odds: {'home': float, 'draw': float, 'away': float, 
                  'over_2.5': float, 'btts_yes': float, etc.}
        
        Returns:
            Dict with probabilities
        """
        # Convert odds to implied probabilities
        def odds_to_prob(odds_value: float) -> float:
            return 1.0 / odds_value if odds_value > 1.0 else 0.5
        
        # 1X2 probabilities
        home_prob = odds_to_prob(odds.get('home', 2.0))
        draw_prob = odds_to_prob(odds.get('draw', 3.5))
        away_prob = odds_to_prob(odds.get('away', 3.0))
        
        # Remove overround (bookmaker margin)
        total_1x2 = home_prob + draw_prob + away_prob
        home_win = home_prob / total_1x2
        draw = draw_prob / total_1x2
        away_win = away_prob / total_1x2
        
        # Over/Under
        over_1_5 = odds_to_prob(odds.get('over_1.5', 1.20))
        over_2_5 = odds_to_prob(odds.get('over_2.5', 1.80))
        over_3_5 = odds_to_prob(odds.get('over_3.5', 3.00))
        
        # BTTS
        btts = odds_to_prob(odds.get('btts_yes', 1.90))
        
        return {
            'home_win': home_win,
            'draw': draw,
            'away_win': away_win,
            'over_1.5': over_1_5,
            'over_2.5': over_2_5,
            'over_3.5': over_3_5,
            'btts': btts
        }
    
    # ==========================================
    # MODEL 4: H2H HISTORICAL
    # ==========================================
    
    def predict_h2h(self, h2h_data: List[Dict]) -> Dict:
        """
        Predictions based on head-to-head history
        
        Args:
            h2h_data: List of past matches
                [{'home_score': int, 'away_score': int, 'date': str}, ...]
        
        Returns:
            Dict with probabilities
        """
        if not h2h_data or len(h2h_data) < 3:
            # Not enough data, return neutral probabilities
            return {
                'home_win': 0.40,
                'draw': 0.30,
                'away_win': 0.30,
                'over_1.5': 0.70,
                'over_2.5': 0.50,
                'over_3.5': 0.30,
                'btts': 0.50
            }
        
        # Analyze last 10 H2H matches (or less if not available)
        recent_h2h = h2h_data[-10:]
        
        home_wins = 0
        draws = 0
        away_wins = 0
        total_goals = []
        btts_count = 0
        
        for match in recent_h2h:
            home_score = match['home_score']
            away_score = match['away_score']
            
            if home_score > away_score:
                home_wins += 1
            elif home_score < away_score:
                away_wins += 1
            else:
                draws += 1
            
            total = home_score + away_score
            total_goals.append(total)
            
            if home_score > 0 and away_score > 0:
                btts_count += 1
        
        n = len(recent_h2h)
        
        return {
            'home_win': home_wins / n,
            'draw': draws / n,
            'away_win': away_wins / n,
            'over_1.5': sum(1 for g in total_goals if g > 1.5) / n,
            'over_2.5': sum(1 for g in total_goals if g > 2.5) / n,
            'over_3.5': sum(1 for g in total_goals if g > 3.5) / n,
            'btts': btts_count / n
        }
    
    # ==========================================
    # ENSEMBLE COMBINATION
    # ==========================================
    
    def predict_ensemble(self, 
                        home_xg: float = None,
                        away_xg: float = None,
                        home_form: Dict = None,
                        away_form: Dict = None,
                        odds: Dict = None,
                        h2h_data: List[Dict] = None,
                        runs: int = 100) -> Dict:
        """
        Combine all models into ensemble prediction
        
        Args:
            home_xg: Home expected goals (for Poisson)
            away_xg: Away expected goals (for Poisson)
            home_form: Home team form data (for ML)
            away_form: Away team form data (for ML)
            odds: Bookmaker odds (for Market)
            h2h_data: Head-to-head history (for H2H)
            runs: Monte Carlo simulations
        
        Returns:
            Dict with ensemble predictions + individual model results
        """
        predictions = {}
        available_models = []
        
        # Run each available model
        if home_xg is not None and away_xg is not None:
            predictions['poisson'] = self.predict_poisson(home_xg, away_xg, runs)
            available_models.append('poisson')
        
        if home_form is not None and away_form is not None:
            predictions['ml_form'] = self.predict_ml_form(home_form, away_form)
            available_models.append('ml_form')
        
        if odds is not None:
            predictions['market'] = self.predict_market_consensus(odds)
            available_models.append('market')
        
        if h2h_data is not None:
            predictions['h2h'] = self.predict_h2h(h2h_data)
            available_models.append('h2h')
        
        if not available_models:
            return {'error': 'No model data provided'}
        
        # Normalize weights for available models
        active_weights = {m: self.weights[m] for m in available_models}
        total_weight = sum(active_weights.values())
        normalized_weights = {m: w/total_weight for m, w in active_weights.items()}
        
        # Combine predictions (weighted average)
        markets = ['home_win', 'draw', 'away_win', 'over_1.5', 'over_2.5', 'over_3.5', 'btts']
        ensemble = {}
        
        for market in markets:
            ensemble[market] = sum(
                predictions[model][market] * normalized_weights[model]
                for model in available_models
            )
        
        # Calculate variance (model agreement)
        variance = {}
        for market in markets:
            values = [predictions[model][market] for model in available_models]
            variance[market] = np.var(values)
        
        # Confidence: Lower variance = higher confidence
        avg_variance = np.mean(list(variance.values()))
        confidence = max(0.5, 1.0 - (avg_variance * 10))  # Scale variance to confidence
        
        return {
            'ensemble': ensemble,
            'individual_models': predictions,
            'weights_used': normalized_weights,
            'model_agreement': {market: 1.0 - var for market, var in variance.items()},
            'confidence': confidence,
            'models_available': len(available_models)
        }
    
    def update_weights(self, model_accuracies: Dict[str, float]) -> None:
        """
        Update model weights based on historical accuracy
        
        Args:
            model_accuracies: {'poisson': 0.65, 'ml_form': 0.70, ...}
        """
        total_accuracy = sum(model_accuracies.values())
        
        for model, accuracy in model_accuracies.items():
            self.weights[model] = accuracy / total_accuracy
        
        self._save_weights()
    
    def _save_weights(self) -> None:
        """Save weights to file"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        data = {
            'weights': self.weights,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.weights_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_weights(self) -> None:
        """Load weights from file"""
        if os.path.exists(self.weights_file):
            with open(self.weights_file, 'r') as f:
                data = json.load(f)
                self.weights = data.get('weights', self.weights)


# =============================================
# DEMO
# =============================================
if __name__ == "__main__":
    print("="*80)
    print("🎯 ENSEMBLE PREDICTOR - Multi-Model Demo")
    print("="*80)
    
    predictor = EnsemblePredictor()
    
    print("\n📊 Testing: Bayern Munich vs Bayer Leverkusen")
    print("-"*80)
    
    # Model 1: Poisson (xG)
    home_xg = 2.1
    away_xg = 1.8
    
    # Model 2: ML Form
    home_form = {
        'recent_goals': 2.4,
        'recent_conceded': 0.8,
        'win_rate': 0.75,
        'form_points': 2.5
    }
    away_form = {
        'recent_goals': 2.0,
        'recent_conceded': 1.2,
        'win_rate': 0.65,
        'form_points': 2.2
    }
    
    # Model 3: Market odds
    odds = {
        'home': 1.80,
        'draw': 3.80,
        'away': 4.50,
        'over_2.5': 1.65,
        'btts_yes': 1.75
    }
    
    # Model 4: H2H
    h2h_data = [
        {'home_score': 2, 'away_score': 1, 'date': '2024-09-01'},
        {'home_score': 3, 'away_score': 2, 'date': '2024-03-15'},
        {'home_score': 1, 'away_score': 1, 'date': '2023-10-20'},
        {'home_score': 2, 'away_score': 0, 'date': '2023-04-10'},
        {'home_score': 4, 'away_score': 2, 'date': '2022-11-05'},
    ]
    
    # Get ensemble prediction
    result = predictor.predict_ensemble(
        home_xg=home_xg,
        away_xg=away_xg,
        home_form=home_form,
        away_form=away_form,
        odds=odds,
        h2h_data=h2h_data
    )
    
    # Print individual models
    print("\n📊 Individual Model Predictions:")
    print("-"*80)
    
    for model_name, preds in result['individual_models'].items():
        print(f"\n{model_name.upper().replace('_', ' ')}:")
        print(f"  Home Win: {preds['home_win']:.1%}")
        print(f"  Draw: {preds['draw']:.1%}")
        print(f"  Away Win: {preds['away_win']:.1%}")
        print(f"  Over 2.5: {preds['over_2.5']:.1%}")
        print(f"  BTTS: {preds['btts']:.1%}")
    
    # Print ensemble
    print("\n" + "="*80)
    print("🎯 ENSEMBLE PREDICTION (Weighted Average)")
    print("="*80)
    
    ens = result['ensemble']
    print(f"\n1X2 Market:")
    print(f"  Home Win: {ens['home_win']:.1%} (confidence: {result['model_agreement']['home_win']:.1%})")
    print(f"  Draw: {ens['draw']:.1%} (confidence: {result['model_agreement']['draw']:.1%})")
    print(f"  Away Win: {ens['away_win']:.1%} (confidence: {result['model_agreement']['away_win']:.1%})")
    
    print(f"\nGoals Market:")
    print(f"  Over 1.5: {ens['over_1.5']:.1%}")
    print(f"  Over 2.5: {ens['over_2.5']:.1%} (confidence: {result['model_agreement']['over_2.5']:.1%})")
    print(f"  Over 3.5: {ens['over_3.5']:.1%}")
    
    print(f"\nBTTS: {ens['btts']:.1%} (confidence: {result['model_agreement']['btts']:.1%})")
    
    print(f"\n📊 Overall Confidence: {result['confidence']:.1%}")
    print(f"📊 Models Used: {result['models_available']}/4")
    
    print("\n💡 Model Weights:")
    for model, weight in result['weights_used'].items():
        print(f"  {model}: {weight:.1%}")
    
    print("\n" + "="*80)
    print("✅ Ensemble Predictor Ready!")
    print("="*80)
