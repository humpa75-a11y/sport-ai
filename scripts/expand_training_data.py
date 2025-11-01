"""
🧠 SYNTHETIC DATA GENERATOR - LEARN FROM EXISTING DATA
======================================================

Strategy:
1. Load existing training data (500 samples we already have)
2. Analyze patterns (score distributions, team strengths, odds)
3. Generate new realistic variations
4. Add noise and variability
5. Expand training set from 500 → 5000+ samples

BLIJF LEREN! 🚀
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import glob
import os
import random

class SyntheticDataGenerator:
    """Generate realistic training data from existing patterns"""
    
    def __init__(self):
        self.existing_data = None
        self.team_profiles = {}
        self.score_distribution = {}
        self.odds_patterns = {}
        
    def load_existing_data(self):
        """Load existing training data"""
        print("\n" + "="*80)
        print("📥 LOADING EXISTING TRAINING DATA")
        print("="*80)
        
        files = glob.glob('data/training_dataset_*.csv')
        
        if not files:
            print("[ERROR] No existing training data found!")
            return None
        
        latest_file = max(files, key=os.path.getctime)
        print(f"[LOAD] File: {latest_file}")
        
        df = pd.read_csv(latest_file)
        print(f"[LOAD] Loaded {len(df)} existing matches")
        
        self.existing_data = df
        return df
    
    def analyze_patterns(self):
        """Analyze existing data patterns"""
        print("\n" + "="*80)
        print("🔍 ANALYZING EXISTING PATTERNS")
        print("="*80)
        
        df = self.existing_data
        
        # 1. Score distribution
        score_counts = {}
        for _, row in df.iterrows():
            score = f"{int(row['home_score'])}-{int(row['away_score'])}"
            score_counts[score] = score_counts.get(score, 0) + 1
        
        total = len(df)
        self.score_distribution = {
            score: count / total 
            for score, count in score_counts.items()
        }
        
        print("\n[PATTERN] Score Distribution (top 10):")
        sorted_scores = sorted(self.score_distribution.items(), key=lambda x: x[1], reverse=True)
        for score, prob in sorted_scores[:10]:
            print(f"  {score}: {prob:.1%}")
        
        # 2. Team strength profiles
        teams = list(set(list(df['home_team'].unique()) + list(df['away_team'].unique())))
        
        for team in teams:
            home_matches = df[df['home_team'] == team]
            away_matches = df[df['away_team'] == team]
            
            home_goals = home_matches['home_score'].mean() if len(home_matches) > 0 else 1.5
            away_goals = away_matches['away_score'].mean() if len(away_matches) > 0 else 1.2
            
            home_conceded = home_matches['away_score'].mean() if len(home_matches) > 0 else 1.0
            away_conceded = away_matches['home_score'].mean() if len(away_matches) > 0 else 1.2
            
            self.team_profiles[team] = {
                'attack_strength': (home_goals + away_goals) / 2,
                'defense_strength': (home_conceded + away_conceded) / 2,
                'home_advantage': home_goals - away_goals if home_goals > 0 and away_goals > 0 else 0.3
            }
        
        print(f"\n[PATTERN] Created {len(self.team_profiles)} team profiles")
        
        # 3. Odds patterns
        if 'home_odds' in df.columns:
            df['goals_total'] = df['home_score'] + df['away_score']
            df['home_win'] = (df['home_score'] > df['away_score']).astype(int)
            
            # Correlation between odds and outcomes
            avg_home_odds_for_win = df[df['home_win'] == 1]['home_odds'].mean()
            avg_home_odds_for_loss = df[df['home_win'] == 0]['home_odds'].mean()
            
            self.odds_patterns = {
                'home_win_odds': avg_home_odds_for_win,
                'home_loss_odds': avg_home_odds_for_loss,
                'draw_odds_avg': df['draw_odds'].mean() if 'draw_odds' in df.columns else 3.2
            }
            
            print(f"\n[PATTERN] Odds patterns:")
            print(f"  Avg home odds when winning: {avg_home_odds_for_win:.2f}")
            print(f"  Avg home odds when losing: {avg_home_odds_for_loss:.2f}")
        
        print("\n[SUCCESS] Pattern analysis complete")
    
    def generate_realistic_match(self):
        """Generate one realistic match based on learned patterns"""
        
        # Pick random teams
        teams = list(self.team_profiles.keys())
        home_team = random.choice(teams)
        away_team = random.choice([t for t in teams if t != home_team])
        
        home_profile = self.team_profiles[home_team]
        away_profile = self.team_profiles[away_team]
        
        # Expected goals based on team strengths (boosted for realism)
        base_home_xg = 1.4  # Average home goals in football
        base_away_xg = 1.1  # Average away goals
        
        home_xg = base_home_xg * home_profile['attack_strength'] * (1 + home_profile['home_advantage']) / away_profile['defense_strength']
        away_xg = base_away_xg * away_profile['attack_strength'] / home_profile['defense_strength']
        
        # Clamp to reasonable range (but higher than before)
        home_xg = max(0.8, min(4.5, home_xg))
        away_xg = max(0.6, min(3.5, away_xg))
        
        # Generate score using Poisson distribution
        home_score = np.random.poisson(home_xg)
        away_score = np.random.poisson(away_xg)
        
        # Cap at 6 goals (rare to score more)
        home_score = min(home_score, 6)
        away_score = min(away_score, 6)
        
        # Generate realistic odds
        # Lower odds = favorite (higher win probability)
        if home_score > away_score:
            # Home won, so home should have been favorite
            home_odds = random.uniform(1.40, 2.50)
            away_odds = random.uniform(2.50, 5.00)
        elif away_score > home_score:
            # Away won
            home_odds = random.uniform(2.50, 5.00)
            away_odds = random.uniform(1.40, 2.50)
        else:
            # Draw
            home_odds = random.uniform(2.20, 3.20)
            away_odds = random.uniform(2.20, 3.20)
        
        draw_odds = random.uniform(3.00, 3.80)
        
        # Random league
        league = random.choice(['Eredivisie', 'Premier League'])
        
        # Random recent date
        days_ago = random.randint(1, 90)
        date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'home_odds': round(home_odds, 2),
            'away_odds': round(away_odds, 2),
            'draw_odds': round(draw_odds, 2),
            'league': league,
            'date': date,
            'source': 'synthetic_learned'
        }
    
    def generate_dataset(self, target_size=5000):
        """Generate large training dataset"""
        print("\n" + "="*80)
        print(f"🎲 GENERATING {target_size} TRAINING SAMPLES")
        print("="*80)
        
        current_size = len(self.existing_data)
        new_samples_needed = max(0, target_size - current_size)
        
        print(f"[INFO] Current dataset: {current_size} samples")
        print(f"[INFO] Target dataset: {target_size} samples")
        print(f"[INFO] Generating: {new_samples_needed} new samples")
        
        new_samples = []
        
        for i in range(new_samples_needed):
            match = self.generate_realistic_match()
            new_samples.append(match)
            
            if (i + 1) % 500 == 0:
                print(f"[PROGRESS] Generated {i + 1}/{new_samples_needed} samples...")
        
        print(f"[SUCCESS] Generated {len(new_samples)} new samples")
        
        # Combine with existing
        new_df = pd.DataFrame(new_samples)
        combined_df = pd.concat([self.existing_data, new_df], ignore_index=True)
        
        print(f"[COMBINE] Total dataset: {len(combined_df)} samples")
        
        return combined_df
    
    def validate_quality(self, df):
        """Validate synthetic data quality"""
        print("\n" + "="*80)
        print("✅ VALIDATING DATA QUALITY")
        print("="*80)
        
        # Check score distribution
        score_counts = {}
        for _, row in df.iterrows():
            score = f"{int(row['home_score'])}-{int(row['away_score'])}"
            score_counts[score] = score_counts.get(score, 0) + 1
        
        print("\n[VALIDATE] New Score Distribution (top 10):")
        sorted_scores = sorted(score_counts.items(), key=lambda x: x[1], reverse=True)
        for score, count in sorted_scores[:10]:
            prob = count / len(df)
            print(f"  {score}: {prob:.1%} ({count} matches)")
        
        # Check average goals
        avg_home_goals = df['home_score'].mean()
        avg_away_goals = df['away_score'].mean()
        avg_total_goals = avg_home_goals + avg_away_goals
        
        print(f"\n[VALIDATE] Average Goals:")
        print(f"  Home: {avg_home_goals:.2f}")
        print(f"  Away: {avg_away_goals:.2f}")
        print(f"  Total: {avg_total_goals:.2f}")
        
        # Expected: 2.4-2.8 goals per match (realistic)
        if 2.2 < avg_total_goals < 3.0:
            print(f"  ✅ REALISTIC (expected 2.4-2.8)")
        else:
            print(f"  ⚠️  WARNING: Outside typical range")
        
        # Check odds distribution
        if 'home_odds' in df.columns:
            avg_home_odds = df['home_odds'].mean()
            avg_away_odds = df['away_odds'].mean()
            
            print(f"\n[VALIDATE] Average Odds:")
            print(f"  Home: {avg_home_odds:.2f}")
            print(f"  Away: {avg_away_odds:.2f}")
            
            # Expected: 2.5-3.0 (balanced)
            if 2.2 < avg_home_odds < 3.5 and 2.2 < avg_away_odds < 3.5:
                print(f"  ✅ REALISTIC")
            else:
                print(f"  ⚠️  WARNING: Unusual odds distribution")
        
        print("\n[SUCCESS] Quality validation complete")
    
    def save_expanded_dataset(self, df):
        """Save expanded dataset"""
        print("\n" + "="*80)
        print("💾 SAVING EXPANDED DATASET")
        print("="*80)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save CSV
        csv_file = f'data/training_dataset_expanded_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        print(f"[SAVE] CSV: {csv_file} ({len(df)} rows)")
        
        # Save JSON
        json_file = f'data/training_dataset_expanded_{timestamp}.json'
        df.to_json(json_file, orient='records', indent=2)
        print(f"[SAVE] JSON: {json_file}")
        
        # Save metadata
        metadata = {
            'created_at': timestamp,
            'total_samples': len(df),
            'original_samples': len(self.existing_data),
            'synthetic_samples': len(df) - len(self.existing_data),
            'teams': list(self.team_profiles.keys()),
            'score_distribution': self.score_distribution,
            'generation_method': 'learned_patterns_poisson'
        }
        
        metadata_file = f'data/training_metadata_{timestamp}.json'
        import json
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"[SAVE] Metadata: {metadata_file}")
        
        print("\n[SUCCESS] All files saved")
        
        return csv_file
    
    def run_expansion(self, target_size=5000):
        """Complete expansion pipeline"""
        print("\n" + "="*80)
        print("🧠 SYNTHETIC DATA EXPANSION PIPELINE")
        print("="*80)
        print(f"Target: {target_size} training samples")
        print("="*80 + "\n")
        
        # Load existing
        df = self.load_existing_data()
        if df is None:
            print("[ERROR] Cannot proceed without existing data")
            return
        
        # Analyze patterns
        self.analyze_patterns()
        
        # Generate new samples
        expanded_df = self.generate_dataset(target_size)
        
        # Validate
        self.validate_quality(expanded_df)
        
        # Save
        output_file = self.save_expanded_dataset(expanded_df)
        
        print("\n" + "="*80)
        print("✅ EXPANSION COMPLETE!")
        print("="*80)
        print(f"Original: {len(df)} samples")
        print(f"Expanded: {len(expanded_df)} samples")
        print(f"Growth: +{len(expanded_df) - len(df)} samples ({((len(expanded_df) - len(df)) / len(df) * 100):.0f}%)")
        print(f"Output: {output_file}")
        print("="*80 + "\n")
        
        print("🎯 NEXT STEP: Retrain model on expanded dataset!")
        print("   python scripts/train_score_predictor.py\n")


def expand_training_data(target_size=5000):
    """Main entry point"""
    generator = SyntheticDataGenerator()
    generator.run_expansion(target_size)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        target = int(sys.argv[1])
        expand_training_data(target)
    else:
        # Default: expand to 5000 samples
        expand_training_data(5000)
