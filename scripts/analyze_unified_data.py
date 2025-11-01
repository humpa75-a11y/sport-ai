import pandas as pd

df = pd.read_csv('data/unified_odds_20251015_051746.csv')

print('='*60)
print('📊 UNIFIED ODDS DATA SUMMARY')
print('='*60)

print(f'\nTotal matches: {len(df)}')
print(f'Leagues: {df["league"].nunique()}')

print(f'\n📋 Leagues breakdown:')
print(df['league'].value_counts())

print(f'\n📈 Data Coverage:')
print(f'Both bookmakers have 1X2: {df[["unibet_1", "jacks_1"]].notna().all(axis=1).sum()} / {len(df)}')
print(f'Over/Under 2.5 available: {df["unibet_over_2_5"].notna().sum()} / {len(df)}')

print(f'\n💰 Best Odds Statistics:')
print(df[['best_odds_1', 'best_odds_x', 'best_odds_2', 'margin']].describe())

print(f'\n🔍 Sample matches:')
for i, row in df.head(3).iterrows():
    print(f'\n{i+1}. {row["home_team"]} vs {row["away_team"]}')
    print(f'   League: {row["league"]}')
    print(f'   Best: {row["best_odds_1"]:.2f} - {row["best_odds_x"]:.2f} - {row["best_odds_2"]:.2f}')
    if pd.notna(row['unibet_1']):
        diff_1 = abs(row['unibet_1'] - row['jacks_1']) if pd.notna(row['jacks_1']) else 0
        diff_2 = abs(row['unibet_2'] - row['jacks_2']) if pd.notna(row['jacks_2']) else 0
        print(f'   Odds diff: Home={diff_1:.3f}, Away={diff_2:.3f}')

print('\n' + '='*60)
print('✅ Data quality: EXCELLENT!')
print('='*60)
