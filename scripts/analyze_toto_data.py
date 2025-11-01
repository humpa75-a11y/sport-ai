"""Quick TOTO data quality analysis"""
import pandas as pd

df = pd.read_csv('data/toto_odds_20251015_054036.csv')

print('\n🎯 TOTO.NL DATA QUALITY REPORT')
print('=' * 80)
print(f'\nTotal matches: {len(df)}')
print(f'With 1X2 odds: {df["odds_1"].notna().sum()} ({df["odds_1"].notna().sum()/len(df)*100:.1f}%)')
print(f'With O/U odds: {df["odds_over"].notna().sum()} ({df["odds_over"].notna().sum()/len(df)*100:.1f}%)')
print(f'With BTTS odds: {df["odds_btts_yes"].notna().sum()} ({df["odds_btts_yes"].notna().sum()/len(df)*100:.1f}%)')

print(f'\nUnique competitions: {df["competition"].nunique()}')
print(f'Unique countries: {df["country"].nunique()}')

print(f'\nAverage margin: {df["margin"].mean():.2f}%')
print(f'Margin range: {df["margin"].min():.2f}% - {df["margin"].max():.2f}%')

print('\n' + '=' * 80)
print('\nTop 10 competitions by matches:')
print(df['competition'].value_counts().head(10))
print('\n' + '=' * 80)

# Sample
print('\nSample matches:')
print(df[['home_team', 'away_team', 'competition', 'country', 'odds_1', 'odds_x', 'odds_2']].head(15).to_string())
