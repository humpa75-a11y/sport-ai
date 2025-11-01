"""
📊 DE MEESTER PERFORMANCE ANALYZER 📊

Analyseert hoe goed De Meester voorspelt:
- Vergelijkt voorspellingen met echte resultaten
- Berekent accuracy, MAE, RMSE
- Genereert uitgebreid rapport
- Track improvement over time

Output: Professioneel analyserap port
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

class MeesterAnalyzer:
    """Analyseert De Meester's performance"""
    
    def __init__(self):
        self.predictions = []
        self.actuals = []
        self.history_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'prediction_history.json')
        
    def load_prediction_history(self):
        """Laad prediction history"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.predictions = json.load(f)
            print(f"Loaded {len(self.predictions)} historical predictions")
        else:
            print("No prediction history found")
            # Genereer sample data voor demo
            self.generate_sample_predictions()
    
    def generate_sample_predictions(self, n=100):
        """Genereer sample predictions voor analyse"""
        print(f"\nGenerating {n} sample predictions for analysis...")
        
        np.random.seed(42)
        
        for i in range(n):
            # Predicted
            pred_home = max(0, np.random.poisson(1.5))
            pred_away = max(0, np.random.poisson(1.2))
            
            # Actual (met wat variatie)
            actual_home = max(0, pred_home + np.random.randint(-1, 2))
            actual_away = max(0, pred_away + np.random.randint(-1, 2))
            
            # Confidence (hoger bij goede voorspellingen)
            diff = abs(pred_home - actual_home) + abs(pred_away - actual_away)
            confidence = max(50, 95 - diff * 10)
            
            prediction = {
                'date': (datetime.now() - timedelta(days=n-i)).isoformat(),
                'home_team': f'Team {i%20 + 1}',
                'away_team': f'Team {(i+10)%20 + 1}',
                'predicted_home_goals': pred_home,
                'predicted_away_goals': pred_away,
                'actual_home_goals': actual_home,
                'actual_away_goals': actual_away,
                'confidence': confidence,
                'correct_winner': self._check_winner(pred_home, pred_away, actual_home, actual_away),
                'exact_score': pred_home == actual_home and pred_away == actual_away
            }
            
            self.predictions.append(prediction)
        
        print(f"Generated {len(self.predictions)} sample predictions")
    
    def _check_winner(self, pred_h, pred_a, act_h, act_a):
        """Check if winner prediction was correct"""
        pred_result = 'H' if pred_h > pred_a else ('D' if pred_h == pred_a else 'A')
        act_result = 'H' if act_h > act_a else ('D' if act_h == act_a else 'A')
        return pred_result == act_result
    
    def calculate_overall_stats(self):
        """Bereken overall statistieken"""
        print("\n" + "="*80)
        print("OVERALL PERFORMANCE STATISTICS")
        print("="*80)
        
        df = pd.DataFrame(self.predictions)
        
        # MAE (Mean Absolute Error)
        mae_home = np.mean(np.abs(df['predicted_home_goals'] - df['actual_home_goals']))
        mae_away = np.mean(np.abs(df['predicted_away_goals'] - df['actual_away_goals']))
        mae_total = (mae_home + mae_away) / 2
        
        # RMSE (Root Mean Squared Error)
        rmse_home = np.sqrt(np.mean((df['predicted_home_goals'] - df['actual_home_goals'])**2))
        rmse_away = np.sqrt(np.mean((df['predicted_away_goals'] - df['actual_away_goals'])**2))
        rmse_total = (rmse_home + rmse_away) / 2
        
        # Accuracy metrics
        winner_accuracy = df['correct_winner'].mean() * 100
        exact_score_accuracy = df['exact_score'].mean() * 100
        
        # Confidence analysis
        avg_confidence = df['confidence'].mean()
        
        # High confidence predictions (>80%)
        high_conf = df[df['confidence'] > 80]
        high_conf_accuracy = high_conf['correct_winner'].mean() * 100 if len(high_conf) > 0 else 0
        
        stats = {
            'total_predictions': len(df),
            'mae_home': mae_home,
            'mae_away': mae_away,
            'mae_total': mae_total,
            'rmse_home': rmse_home,
            'rmse_away': rmse_away,
            'rmse_total': rmse_total,
            'winner_accuracy': winner_accuracy,
            'exact_score_accuracy': exact_score_accuracy,
            'avg_confidence': avg_confidence,
            'high_confidence_predictions': len(high_conf),
            'high_confidence_accuracy': high_conf_accuracy
        }
        
        # Print stats
        print(f"\n📊 PREDICTIONS: {stats['total_predictions']}")
        print(f"\n🎯 ACCURACY:")
        print(f"  Winner Prediction:  {stats['winner_accuracy']:.1f}%")
        print(f"  Exact Score:        {stats['exact_score_accuracy']:.1f}%")
        print(f"\n📈 ERROR METRICS:")
        print(f"  MAE (Total):        {stats['mae_total']:.3f} goals")
        print(f"  MAE (Home):         {stats['mae_home']:.3f} goals")
        print(f"  MAE (Away):         {stats['mae_away']:.3f} goals")
        print(f"  RMSE (Total):       {stats['rmse_total']:.3f} goals")
        print(f"\n💪 CONFIDENCE ANALYSIS:")
        print(f"  Avg Confidence:     {stats['avg_confidence']:.1f}%")
        print(f"  High Conf (>80%):   {stats['high_confidence_predictions']} predictions")
        print(f"  High Conf Accuracy: {stats['high_confidence_accuracy']:.1f}%")
        
        return stats
    
    def analyze_by_goal_range(self):
        """Analyseer performance per doelpunten categorie"""
        print("\n" + "="*80)
        print("PERFORMANCE BY GOAL RANGE")
        print("="*80)
        
        df = pd.DataFrame(self.predictions)
        df['total_goals'] = df['actual_home_goals'] + df['actual_away_goals']
        
        ranges = [
            ('Low (0-1)', 0, 1),
            ('Medium (2-3)', 2, 3),
            ('High (4+)', 4, 10)
        ]
        
        for label, min_goals, max_goals in ranges:
            subset = df[(df['total_goals'] >= min_goals) & (df['total_goals'] <= max_goals)]
            
            if len(subset) > 0:
                accuracy = subset['correct_winner'].mean() * 100
                mae = np.mean(np.abs(subset['predicted_home_goals'] - subset['actual_home_goals']) + 
                             np.abs(subset['predicted_away_goals'] - subset['actual_away_goals']))
                
                print(f"\n{label} goals:")
                print(f"  Matches:   {len(subset)}")
                print(f"  Accuracy:  {accuracy:.1f}%")
                print(f"  MAE:       {mae:.3f}")
    
    def generate_improvement_recommendations(self, stats):
        """Genereer verbeteringssuggesti es"""
        print("\n" + "="*80)
        print("🚀 IMPROVEMENT RECOMMENDATIONS")
        print("="*80)
        
        recommendations = []
        
        # Check MAE
        if stats['mae_total'] > 1.2:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Prediction Accuracy',
                'issue': f"MAE is hoog ({stats['mae_total']:.2f} goals)",
                'action': 'Train model op meer recente data, voeg extra features toe'
            })
        elif stats['mae_total'] > 0.9:
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Prediction Accuracy',
                'issue': f"MAE kan beter ({stats['mae_total']:.2f} goals)",
                'action': 'Optimaliseer hyperparameters, probeer ensemble methods'
            })
        else:
            recommendations.append({
                'priority': 'LOW',
                'area': 'Prediction Accuracy',
                'issue': f"MAE is goed ({stats['mae_total']:.2f} goals)",
                'action': 'Behoud huidige aanpak, monitor performance'
            })
        
        # Check winner accuracy
        if stats['winner_accuracy'] < 50:
            recommendations.append({
                'priority': 'CRITICAL',
                'area': 'Winner Prediction',
                'issue': f"Winner accuracy te laag ({stats['winner_accuracy']:.1f}%)",
                'action': 'Model opnieuw trainen, check data quality'
            })
        elif stats['winner_accuracy'] < 60:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'Winner Prediction',
                'issue': f"Winner accuracy onder gemiddeld ({stats['winner_accuracy']:.1f}%)",
                'action': 'Voeg team form features toe, verbeter data kwaliteit'
            })
        
        # Check confidence calibration
        if stats['high_confidence_accuracy'] < stats['winner_accuracy']:
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'Confidence Calibration',
                'issue': 'Hoge confidence voorspellingen presteren slechter',
                'action': 'Herzie confidence score berekening'
            })
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. [{rec['priority']}] {rec['area']}")
            print(f"   Issue:  {rec['issue']}")
            print(f"   Action: {rec['action']}")
        
        return recommendations
    
    def generate_html_report(self, stats, recommendations):
        """Genereer HTML rapport"""
        print("\n" + "="*80)
        print("GENERATING HTML REPORT")
        print("="*80)
        
        # Bepaal rating
        if stats['mae_total'] < 0.8 and stats['winner_accuracy'] > 60:
            rating = "EXCELLENT"
            color = "#10b981"
        elif stats['mae_total'] < 1.0 and stats['winner_accuracy'] > 55:
            rating = "GOOD"
            color = "#3b82f6"
        elif stats['mae_total'] < 1.2 and stats['winner_accuracy'] > 50:
            rating = "AVERAGE"
            color = "#f59e0b"
        else:
            rating = "NEEDS IMPROVEMENT"
            color = "#ef4444"
        
        html = f"""
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>De Meester Performance Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            margin: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid {color};
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 42px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .rating {{
            display: inline-block;
            background: {color};
            color: white;
            padding: 10px 30px;
            border-radius: 25px;
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .stat-label {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }}
        .section {{
            margin: 40px 0;
        }}
        .section h2 {{
            color: #667eea;
            border-left: 5px solid #764ba2;
            padding-left: 15px;
            margin-bottom: 20px;
        }}
        .recommendation {{
            background: #f8f9fa;
            padding: 15px;
            margin: 15px 0;
            border-left: 4px solid #667eea;
            border-radius: 8px;
        }}
        .priority-high {{
            border-left-color: #ef4444;
        }}
        .priority-medium {{
            border-left-color: #f59e0b;
        }}
        .priority-low {{
            border-left-color: #10b981;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 DE MEESTER</h1>
            <p style="font-size: 18px; color: #666;">Performance Analysis Report</p>
            <div class="rating">{rating}</div>
            <p style="color: #999; margin-top: 20px;">Generated: {datetime.now().strftime('%d-%m-%Y %H:%M')}</p>
        </div>
        
        <div class="section">
            <h2>📊 Key Performance Indicators</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Total Predictions</div>
                    <div class="stat-value">{stats['total_predictions']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Winner Accuracy</div>
                    <div class="stat-value">{stats['winner_accuracy']:.1f}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Exact Score</div>
                    <div class="stat-value">{stats['exact_score_accuracy']:.1f}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Average Error (MAE)</div>
                    <div class="stat-value">{stats['mae_total']:.2f}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Detailed Metrics</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background: #f8f9fa;">
                    <th style="padding: 12px; text-align: left; border-bottom: 2px solid #667eea;">Metric</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #667eea;">Value</th>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">Home Goals MAE</td>
                    <td style="padding: 12px; text-align: right; border-bottom: 1px solid #e0e0e0;">{stats['mae_home']:.3f}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">Away Goals MAE</td>
                    <td style="padding: 12px; text-align: right; border-bottom: 1px solid #e0e0e0;">{stats['mae_away']:.3f}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">RMSE Total</td>
                    <td style="padding: 12px; text-align: right; border-bottom: 1px solid #e0e0e0;">{stats['rmse_total']:.3f}</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">Average Confidence</td>
                    <td style="padding: 12px; text-align: right; border-bottom: 1px solid #e0e0e0;">{stats['avg_confidence']:.1f}%</td>
                </tr>
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #e0e0e0;">High Confidence Predictions</td>
                    <td style="padding: 12px; text-align: right; border-bottom: 1px solid #e0e0e0;">{stats['high_confidence_predictions']}</td>
                </tr>
                <tr>
                    <td style="padding: 12px;">High Confidence Accuracy</td>
                    <td style="padding: 12px; text-align: right;">{stats['high_confidence_accuracy']:.1f}%</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>🚀 Recommendations</h2>
"""
        
        for rec in recommendations:
            priority_class = f"priority-{rec['priority'].lower()}"
            html += f"""
            <div class="recommendation {priority_class}">
                <strong>[{rec['priority']}] {rec['area']}</strong>
                <p style="margin: 8px 0;"><em>{rec['issue']}</em></p>
                <p style="margin: 8px 0;">💡 <strong>Action:</strong> {rec['action']}</p>
            </div>
"""
        
        html += """
        </div>
        
        <div class="footer">
            <p><strong>De Meester AI</strong> - Ultimate Score Prediction System</p>
            <p style="font-size: 12px; margin-top: 10px;">Keep training, keep improving! 🎯</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Save HTML
        report_file = os.path.join(os.path.dirname(__file__), '..', 'reports', f'meester_performance_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Report saved: {report_file}")
        return report_file
    
    def run_full_analysis(self):
        """RUN complete analysis"""
        print("\n" + "="*80)
        print("📊 DE MEESTER PERFORMANCE ANALYZER")
        print("="*80)
        print(f"Start: {datetime.now()}")
        
        # Load data
        self.load_prediction_history()
        
        # Calculate stats
        stats = self.calculate_overall_stats()
        
        # Analyze by goal range
        self.analyze_by_goal_range()
        
        # Generate recommendations
        recommendations = self.generate_improvement_recommendations(stats)
        
        # Generate HTML report
        report_file = self.generate_html_report(stats, recommendations)
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE!")
        print("="*80)
        print(f"End: {datetime.now()}")
        print(f"\nReport: {report_file}")
        
        return report_file


if __name__ == '__main__':
    analyzer = MeesterAnalyzer()
    report = analyzer.run_full_analysis()
    
    print(f"\n✅ SUCCESS!")
    print(f"Open report in browser: {report}")
