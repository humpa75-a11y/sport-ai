"""
📊 PREDICTION TRACKER - Historical Accuracy & Performance

Features:
- Track alle predictions vs actual results
- Accuracy per market (1X2, Over/Under, BTTS)
- Calibration curves (is 70% confidence echt 70%?)
- ROI tracking per bet type
- Performance reports

Author: Sport AI Sync
Date: November 2025
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import numpy as np


class PredictionTracker:
    """
    Track predictions en vergelijk met actual results
    
    Metrics:
    - Accuracy per market
    - Calibration (predicted prob vs actual outcome)
    - ROI per market type
    - Confidence intervals
    - Trend analysis
    """
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.predictions_file = os.path.join(self.data_dir, 'prediction_tracker.json')
        self.predictions = []
        
        self._load_data()
    
    def log_prediction(self, match_id: str, match_name: str, match_date: str,
                      market: str, prediction: str, probability: float,
                      odds: float, confidence: float) -> None:
        """
        Log een nieuwe prediction
        
        Args:
            match_id: Unique match identifier
            match_name: "Team A vs Team B"
            match_date: YYYY-MM-DD
            market: Market type (1X2, Over/Under, BTTS, etc.)
            prediction: Predicted outcome
            probability: Win probability (0-1)
            odds: Decimal odds
            confidence: Model confidence (0-100)
        """
        pred = {
            'match_id': match_id,
            'match_name': match_name,
            'match_date': match_date,
            'market': market,
            'prediction': prediction,
            'probability': probability,
            'odds': odds,
            'confidence': confidence,
            'ev': (probability * (odds - 1)) - (1 - probability),
            'logged_at': datetime.now().isoformat(),
            'status': 'pending',
            'actual_result': None,
            'correct': None,
            'settled_at': None
        }
        
        self.predictions.append(pred)
        self._save_data()
    
    def settle_prediction(self, match_id: str, actual_result: str, 
                         actual_score: Optional[str] = None) -> Dict:
        """
        Settle een prediction met actual result
        
        Args:
            match_id: Match identifier
            actual_result: Actual outcome (moet matchen met prediction options)
            actual_score: Optional actual score (e.g., "3-1")
        
        Returns:
            Settled prediction data
        """
        # Find all predictions for this match
        settled = []
        
        for pred in self.predictions:
            if pred['match_id'] == match_id and pred['status'] == 'pending':
                pred['actual_result'] = actual_result
                pred['actual_score'] = actual_score
                pred['correct'] = (pred['prediction'] == actual_result)
                pred['status'] = 'settled'
                pred['settled_at'] = datetime.now().isoformat()
                
                settled.append(pred)
        
        self._save_data()
        
        return {
            'match_id': match_id,
            'settled_count': len(settled),
            'predictions': settled
        }
    
    def get_accuracy_by_market(self) -> Dict:
        """
        Bereken accuracy per market type
        
        Returns:
            Dict met accuracy per market
        """
        df = pd.DataFrame([p for p in self.predictions if p['status'] == 'settled'])
        
        if df.empty:
            return {'message': 'No settled predictions yet'}
        
        # Group by market
        market_stats = df.groupby('market').agg({
            'correct': ['sum', 'count', 'mean'],
            'probability': 'mean',
            'odds': 'mean',
            'confidence': 'mean'
        }).round(4)
        
        # Calculate ROI (simulate €10 bets)
        results = {}
        for market in df['market'].unique():
            market_df = df[df['market'] == market]
            
            total_staked = len(market_df) * 10  # €10 per bet
            total_return = sum(
                10 * row['odds'] if row['correct'] else 0 
                for _, row in market_df.iterrows()
            )
            profit = total_return - total_staked
            roi = (profit / total_staked) * 100 if total_staked > 0 else 0
            
            results[market] = {
                'total_predictions': int(market_stats.loc[market, ('correct', 'count')]),
                'correct': int(market_stats.loc[market, ('correct', 'sum')]),
                'accuracy': float(market_stats.loc[market, ('correct', 'mean')] * 100),
                'avg_probability': float(market_stats.loc[market, ('probability', 'mean')]),
                'avg_odds': float(market_stats.loc[market, ('odds', 'mean')]),
                'avg_confidence': float(market_stats.loc[market, ('confidence', 'mean')]),
                'total_staked': total_staked,
                'total_return': round(total_return, 2),
                'profit': round(profit, 2),
                'roi': round(roi, 2)
            }
        
        return results
    
    def get_calibration_curve(self, bins: int = 10) -> Dict:
        """
        Calibration curve: zijn 70% predictions echt 70% correct?
        
        Args:
            bins: Aantal confidence bins (default: 10)
        
        Returns:
            Dict met calibration data
        """
        df = pd.DataFrame([p for p in self.predictions if p['status'] == 'settled'])
        
        if df.empty:
            return {'message': 'No settled predictions yet'}
        
        # Create confidence bins
        df['conf_bin'] = pd.cut(df['confidence'], bins=bins)
        
        calibration = df.groupby('conf_bin').agg({
            'correct': ['mean', 'count'],
            'confidence': 'mean'
        }).reset_index()
        
        calibration.columns = ['bin', 'actual_accuracy', 'count', 'predicted_confidence']
        
        # Calculate calibration error (absolute difference)
        calibration['calibration_error'] = abs(
            calibration['actual_accuracy'] - (calibration['predicted_confidence'] / 100)
        )
        
        # Overall calibration metrics
        mean_calibration_error = calibration['calibration_error'].mean()
        
        return {
            'calibration_data': calibration.to_dict('records'),
            'mean_calibration_error': round(mean_calibration_error, 4),
            'interpretation': (
                '✅ Well calibrated (error < 0.05)' if mean_calibration_error < 0.05
                else '⚠️ Needs calibration (error 0.05-0.10)' if mean_calibration_error < 0.10
                else '🔴 Poorly calibrated (error > 0.10)'
            )
        }
    
    def get_performance_summary(self) -> Dict:
        """
        Complete performance summary
        
        Returns:
            Comprehensive stats dict
        """
        df = pd.DataFrame(self.predictions)
        
        if df.empty:
            return {'message': 'No predictions logged yet'}
        
        total_predictions = len(df)
        pending = len(df[df['status'] == 'pending'])
        settled = len(df[df['status'] == 'settled'])
        
        if settled == 0:
            return {
                'total_predictions': total_predictions,
                'pending': pending,
                'settled': 0,
                'message': 'No settled predictions yet'
            }
        
        settled_df = df[df['status'] == 'settled'].copy()
        
        # Overall accuracy
        overall_accuracy = settled_df['correct'].mean() * 100
        
        # By confidence level
        high_conf = settled_df[settled_df['confidence'] >= 70]
        med_conf = settled_df[(settled_df['confidence'] >= 50) & (settled_df['confidence'] < 70)]
        low_conf = settled_df[settled_df['confidence'] < 50]
        
        # ROI calculation
        total_staked = len(settled_df) * 10
        total_return = sum(
            10 * row['odds'] if row['correct'] else 0 
            for _, row in settled_df.iterrows()
        )
        profit = total_return - total_staked
        roi = (profit / total_staked) * 100
        
        # Best/worst predictions
        best_pred = settled_df.loc[settled_df[settled_df['correct']]['ev'].idxmax()] if settled_df['correct'].any() else None
        worst_pred = settled_df.loc[settled_df[~settled_df['correct']]['ev'].idxmax()] if (~settled_df['correct']).any() else None
        
        return {
            'total_predictions': total_predictions,
            'pending': pending,
            'settled': settled,
            'overall_accuracy': round(overall_accuracy, 2),
            'confidence_breakdown': {
                'high_confidence': {
                    'count': len(high_conf),
                    'accuracy': round(high_conf['correct'].mean() * 100, 2) if len(high_conf) > 0 else 0
                },
                'medium_confidence': {
                    'count': len(med_conf),
                    'accuracy': round(med_conf['correct'].mean() * 100, 2) if len(med_conf) > 0 else 0
                },
                'low_confidence': {
                    'count': len(low_conf),
                    'accuracy': round(low_conf['correct'].mean() * 100, 2) if len(low_conf) > 0 else 0
                }
            },
            'financial_performance': {
                'total_staked': total_staked,
                'total_return': round(total_return, 2),
                'profit': round(profit, 2),
                'roi': round(roi, 2)
            },
            'best_prediction': {
                'match': best_pred['match_name'],
                'market': best_pred['market'],
                'ev': round(best_pred['ev'], 4),
                'odds': best_pred['odds']
            } if best_pred is not None else None,
            'worst_prediction': {
                'match': worst_pred['match_name'],
                'market': worst_pred['market'],
                'ev': round(worst_pred['ev'], 4),
                'odds': worst_pred['odds']
            } if worst_pred is not None else None
        }
    
    def get_trend_analysis(self, last_n: int = 50) -> Dict:
        """
        Analyse trend van laatste N predictions
        
        Args:
            last_n: Aantal laatste predictions te analyseren
        
        Returns:
            Trend analysis dict
        """
        df = pd.DataFrame([p for p in self.predictions if p['status'] == 'settled'])
        
        if df.empty or len(df) < 10:
            return {'message': 'Not enough data for trend analysis (min 10 settled)'}
        
        # Take last N
        recent = df.tail(last_n).copy()
        
        # Calculate rolling accuracy (window=10)
        recent['rolling_accuracy'] = recent['correct'].rolling(window=10, min_periods=5).mean() * 100
        
        # Trend direction
        first_half_accuracy = recent.iloc[:len(recent)//2]['correct'].mean() * 100
        second_half_accuracy = recent.iloc[len(recent)//2:]['correct'].mean() * 100
        
        trend = second_half_accuracy - first_half_accuracy
        
        return {
            'last_n_predictions': len(recent),
            'overall_accuracy': round(recent['correct'].mean() * 100, 2),
            'first_half_accuracy': round(first_half_accuracy, 2),
            'second_half_accuracy': round(second_half_accuracy, 2),
            'trend': round(trend, 2),
            'trend_direction': (
                '📈 Improving' if trend > 5 
                else '📉 Declining' if trend < -5 
                else '➡️ Stable'
            ),
            'recent_form': (
                '🔥 Hot' if second_half_accuracy > 60 
                else '❄️ Cold' if second_half_accuracy < 40 
                else '⚡ Average'
            )
        }
    
    def export_to_csv(self, filename: str = 'prediction_history.csv') -> str:
        """Export predictions to CSV"""
        df = pd.DataFrame(self.predictions)
        filepath = os.path.join(self.data_dir, filename)
        df.to_csv(filepath, index=False)
        return filepath
    
    def _save_data(self) -> None:
        """Save predictions to file"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        data = {
            'predictions': self.predictions,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.predictions_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load predictions from file"""
        if os.path.exists(self.predictions_file):
            with open(self.predictions_file, 'r') as f:
                data = json.load(f)
                self.predictions = data.get('predictions', [])


# =============================================
# DEMO / TEST
# =============================================
if __name__ == "__main__":
    print("="*80)
    print("📊 PREDICTION TRACKER - Historical Accuracy Demo")
    print("="*80)
    
    tracker = PredictionTracker()
    
    # Simulate some predictions
    print("\n📝 Logging predictions...")
    
    # Prediction 1
    tracker.log_prediction(
        match_id='BUN_2025_001',
        match_name='Bayern Munich vs Bayer Leverkusen',
        match_date='2025-11-01',
        market='Over 2.5',
        prediction='Over 2.5',
        probability=0.78,
        odds=1.80,
        confidence=78.2
    )
    
    # Prediction 2
    tracker.log_prediction(
        match_id='BUN_2025_002',
        match_name='RB Leipzig vs VfB Stuttgart',
        match_date='2025-11-02',
        market='BTTS',
        prediction='BTTS Yes',
        probability=0.72,
        odds=1.75,
        confidence=72.5
    )
    
    print(f"✅ Logged {len(tracker.predictions)} predictions")
    
    print("\n" + "="*80)
    print("📊 Performance Summary")
    print("="*80)
    
    summary = tracker.get_performance_summary()
    
    for key, value in summary.items():
        if isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")
    
    print("\n" + "="*80)
    print("✅ Prediction Tracker Ready!")
    print("="*80)
