"""
📊 CALIBRATION ANALYZER - Probability Calibration

Check if our predicted probabilities match reality:
- If we predict 70%, do we win 70% of the time?
- Calibration curves for each model
- Brier score calculation
- Model reliability metrics

Author: Sport AI Sync  
Date: November 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import json
import os
from datetime import datetime
from collections import defaultdict


class CalibrationAnalyzer:
    """
    Analyze prediction calibration
    
    Calibration = Do predicted probabilities match actual outcomes?
    
    Perfect calibration: 70% predictions → 70% success rate
    """
    
    def __init__(self):
        """Initialize calibration analyzer"""
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.calibration_file = os.path.join(self.data_dir, 'calibration_data.json')
        self.calibration_data = []
        
        self._load_data()
    
    def log_prediction(self, predicted_prob: float, actual_outcome: bool,
                      market: str, model: str = 'ensemble') -> None:
        """
        Log a prediction for calibration analysis
        
        Args:
            predicted_prob: Predicted probability (0.0-1.0)
            actual_outcome: Did it happen? (True/False)
            market: Market type ('home_win', 'over_2.5', 'btts', etc.)
            model: Model name ('poisson', 'ensemble', etc.)
        """
        entry = {
            'predicted_prob': predicted_prob,
            'actual_outcome': 1 if actual_outcome else 0,
            'market': market,
            'model': model,
            'timestamp': datetime.now().isoformat()
        }
        
        self.calibration_data.append(entry)
        self._save_data()
    
    def calculate_calibration_curve(self, model: str = None, 
                                    market: str = None,
                                    n_bins: int = 10) -> Dict:
        """
        Calculate calibration curve
        
        Args:
            model: Filter by model (None = all)
            market: Filter by market (None = all)
            n_bins: Number of probability bins
        
        Returns:
            Dict with calibration curve data
        """
        # Filter data
        filtered = self.calibration_data
        
        if model:
            filtered = [d for d in filtered if d['model'] == model]
        
        if market:
            filtered = [d for d in filtered if d['market'] == market]
        
        if len(filtered) < 10:
            return {
                'error': 'Not enough data',
                'data_points': len(filtered),
                'min_required': 10
            }
        
        df = pd.DataFrame(filtered)
        
        # Create probability bins (0-10%, 10-20%, ..., 90-100%)
        bins = np.linspace(0, 1, n_bins + 1)
        df['bin'] = pd.cut(df['predicted_prob'], bins=bins, include_lowest=True)
        
        # Calculate actual success rate per bin
        calibration = []
        
        for bin_range in df['bin'].cat.categories:
            bin_data = df[df['bin'] == bin_range]
            
            if len(bin_data) == 0:
                continue
            
            predicted_prob = bin_data['predicted_prob'].mean()
            actual_rate = bin_data['actual_outcome'].mean()
            count = len(bin_data)
            
            calibration.append({
                'predicted': predicted_prob,
                'actual': actual_rate,
                'count': count,
                'bin_range': f"{bin_range.left:.0%}-{bin_range.right:.0%}"
            })
        
        # Calculate calibration score (how close to diagonal)
        if calibration:
            calibration_error = np.mean([
                abs(c['predicted'] - c['actual']) for c in calibration
            ])
        else:
            calibration_error = 0
        
        return {
            'calibration_curve': calibration,
            'calibration_error': calibration_error,
            'data_points': len(filtered),
            'model': model or 'all',
            'market': market or 'all'
        }
    
    def calculate_brier_score(self, model: str = None, 
                             market: str = None) -> float:
        """
        Calculate Brier score (lower = better)
        
        Brier Score = mean((predicted - actual)^2)
        Perfect score = 0.0, worst = 1.0
        
        Args:
            model: Filter by model
            market: Filter by market
        
        Returns:
            Brier score
        """
        filtered = self.calibration_data
        
        if model:
            filtered = [d for d in filtered if d['model'] == model]
        
        if market:
            filtered = [d for d in filtered if d['market'] == market]
        
        if not filtered:
            return None
        
        predictions = [d['predicted_prob'] for d in filtered]
        outcomes = [d['actual_outcome'] for d in filtered]
        
        brier = np.mean([(p - o)**2 for p, o in zip(predictions, outcomes)])
        
        return brier
    
    def get_calibration_by_model(self, n_bins: int = 10) -> Dict:
        """
        Get calibration curves for all models
        
        Args:
            n_bins: Number of bins
        
        Returns:
            Dict with calibration per model
        """
        models = set(d['model'] for d in self.calibration_data)
        
        results = {}
        for model in models:
            curve = self.calculate_calibration_curve(
                model=model, 
                n_bins=n_bins
            )
            brier = self.calculate_brier_score(model=model)
            
            results[model] = {
                'calibration_curve': curve,
                'brier_score': brier
            }
        
        return results
    
    def get_calibration_by_market(self, n_bins: int = 10) -> Dict:
        """
        Get calibration curves for all markets
        
        Args:
            n_bins: Number of bins
        
        Returns:
            Dict with calibration per market
        """
        markets = set(d['market'] for d in self.calibration_data)
        
        results = {}
        for market in markets:
            curve = self.calculate_calibration_curve(
                market=market,
                n_bins=n_bins
            )
            brier = self.calculate_brier_score(market=market)
            
            results[market] = {
                'calibration_curve': curve,
                'brier_score': brier
            }
        
        return results
    
    def get_reliability_metrics(self) -> Dict:
        """
        Get overall reliability metrics
        
        Returns:
            Dict with metrics
        """
        if not self.calibration_data:
            return {'error': 'No data available'}
        
        df = pd.DataFrame(self.calibration_data)
        
        # Group by confidence levels
        confidence_levels = {
            'High (>70%)': df[df['predicted_prob'] > 0.70],
            'Medium (50-70%)': df[(df['predicted_prob'] >= 0.50) & (df['predicted_prob'] <= 0.70)],
            'Low (<50%)': df[df['predicted_prob'] < 0.50]
        }
        
        metrics = {}
        
        for level, data in confidence_levels.items():
            if len(data) == 0:
                continue
            
            metrics[level] = {
                'count': len(data),
                'avg_predicted': data['predicted_prob'].mean(),
                'actual_success_rate': data['actual_outcome'].mean(),
                'calibration_gap': abs(data['predicted_prob'].mean() - data['actual_outcome'].mean())
            }
        
        # Overall Brier score
        overall_brier = self.calculate_brier_score()
        
        # Overall calibration error
        overall_curve = self.calculate_calibration_curve()
        overall_error = overall_curve.get('calibration_error', 0)
        
        return {
            'by_confidence_level': metrics,
            'overall_brier_score': overall_brier,
            'overall_calibration_error': overall_error,
            'total_predictions': len(self.calibration_data),
            'interpretation': self._interpret_brier(overall_brier)
        }
    
    def _interpret_brier(self, brier: float) -> str:
        """
        Interpret Brier score
        
        Args:
            brier: Brier score value
        
        Returns:
            Interpretation string
        """
        if brier is None:
            return "No data"
        elif brier < 0.10:
            return "🌟 EXCELLENT - Very well calibrated"
        elif brier < 0.15:
            return "✅ GOOD - Well calibrated"
        elif brier < 0.20:
            return "⚠️ FAIR - Needs improvement"
        elif brier < 0.25:
            return "❌ POOR - Poorly calibrated"
        else:
            return "💀 VERY POOR - Major calibration issues"
    
    def export_calibration_plot_data(self, filename: str = 'calibration_plot.json') -> str:
        """
        Export data for plotting calibration curves
        
        Args:
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        by_model = self.get_calibration_by_model()
        by_market = self.get_calibration_by_market()
        overall_metrics = self.get_reliability_metrics()
        
        export_data = {
            'by_model': by_model,
            'by_market': by_market,
            'overall_metrics': overall_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        filepath = os.path.join(self.data_dir, filename)
        os.makedirs(self.data_dir, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filepath
    
    def _save_data(self) -> None:
        """Save calibration data to file"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        data = {
            'calibration_data': self.calibration_data,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.calibration_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_data(self) -> None:
        """Load calibration data from file"""
        if os.path.exists(self.calibration_file):
            with open(self.calibration_file, 'r') as f:
                data = json.load(f)
                self.calibration_data = data.get('calibration_data', [])


# =============================================
# DEMO
# =============================================
if __name__ == "__main__":
    print("="*80)
    print("📊 CALIBRATION ANALYZER - Demo")
    print("="*80)
    
    analyzer = CalibrationAnalyzer()
    
    print("\n📝 Simulating 100 predictions with known outcomes...")
    print("-"*80)
    
    # Simulate well-calibrated predictions
    np.random.seed(42)
    
    for i in range(100):
        # Generate predictions at different probability levels
        if i < 30:
            # High confidence predictions (70-90%)
            pred_prob = np.random.uniform(0.70, 0.90)
            # Should win ~80% of the time
            actual = np.random.random() < pred_prob
            market = 'home_win'
        elif i < 60:
            # Medium confidence (50-70%)
            pred_prob = np.random.uniform(0.50, 0.70)
            actual = np.random.random() < pred_prob
            market = 'over_2.5'
        else:
            # Lower confidence (<50%)
            pred_prob = np.random.uniform(0.30, 0.50)
            actual = np.random.random() < pred_prob
            market = 'btts'
        
        # Alternate between models
        model = 'ensemble' if i % 2 == 0 else 'poisson'
        
        analyzer.log_prediction(pred_prob, actual, market, model)
    
    print("✅ 100 predictions logged")
    
    # Calculate calibration curve
    print("\n" + "="*80)
    print("📊 CALIBRATION CURVE (Overall)")
    print("="*80)
    
    curve_data = analyzer.calculate_calibration_curve(n_bins=10)
    
    if 'error' not in curve_data:
        print(f"\n{'Predicted':<12} {'Actual':<12} {'Count':<10} {'Gap':<10}")
        print("-"*45)
        
        for point in curve_data['calibration_curve']:
            predicted = point['predicted']
            actual = point['actual']
            count = point['count']
            gap = abs(predicted - actual)
            
            print(f"{predicted:>10.1%}  {actual:>10.1%}  {count:>8}  {gap:>8.1%}")
        
        print(f"\n📊 Calibration Error: {curve_data['calibration_error']:.2%}")
    
    # Brier score
    print("\n" + "="*80)
    print("🎯 BRIER SCORE")
    print("="*80)
    
    brier = analyzer.calculate_brier_score()
    print(f"\nOverall Brier Score: {brier:.4f}")
    print(analyzer._interpret_brier(brier))
    print("\nBrier Score Scale:")
    print("  0.00-0.10: EXCELLENT")
    print("  0.10-0.15: GOOD")
    print("  0.15-0.20: FAIR")
    print("  0.20+: POOR")
    
    # Reliability metrics
    print("\n" + "="*80)
    print("📊 RELIABILITY METRICS")
    print("="*80)
    
    metrics = analyzer.get_reliability_metrics()
    
    if 'by_confidence_level' in metrics:
        print("\nBy Confidence Level:")
        print("-"*80)
        
        for level, data in metrics['by_confidence_level'].items():
            print(f"\n{level}:")
            print(f"  Count: {data['count']}")
            print(f"  Avg Predicted: {data['avg_predicted']:.1%}")
            print(f"  Actual Success: {data['actual_success_rate']:.1%}")
            print(f"  Calibration Gap: {data['calibration_gap']:.1%}")
    
    # By model
    print("\n" + "="*80)
    print("📊 CALIBRATION BY MODEL")
    print("="*80)
    
    by_model = analyzer.get_calibration_by_model(n_bins=10)
    
    for model, data in by_model.items():
        print(f"\n{model.upper()}:")
        if data['brier_score'] is not None:
            print(f"  Brier Score: {data['brier_score']:.4f}")
            print(f"  {analyzer._interpret_brier(data['brier_score'])}")
    
    # Export
    print("\n" + "="*80)
    print("💾 Exporting calibration data...")
    filepath = analyzer.export_calibration_plot_data()
    print(f"✅ Exported to: {filepath}")
    
    print("\n" + "="*80)
    print("✅ Calibration Analyzer Ready!")
    print("="*80)
    print("\n💡 Use this to:")
    print("  - Check if your predictions are well-calibrated")
    print("  - Identify which models need adjustment")
    print("  - Compare calibration across markets")
    print("  - Track improvement over time")
