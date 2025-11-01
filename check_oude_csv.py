#!/usr/bin/env python3
"""
🔍 CSV DATA CHECKER 🔍
Controleert hoeveel data er in de oude CSV files zit
"""

import os
import pandas as pd
from glob import glob

print("\n" + "="*80)
print("🔍 CONTROLEREN OUDE CSV DATA")
print("="*80 + "\n")

# 1. Check root directory CSV's
print("📊 ROOT DIRECTORY CSV FILES:\n")

root_csvs = [
    "arbitrage_20251013_194551.csv",
    "best_odds_20251013_194551.csv",
    "odds_20251013_190247.csv",
    "odds_latest.csv",
    "value_bets_20251013_194551.csv"
]

total_root_rows = 0
for csv_file in root_csvs:
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            print(f"   {csv_file}:")
            print(f"      Rijen: {len(df)}")
            print(f"      Kolommen: {list(df.columns)[:5]}...")
            total_root_rows += len(df)
            print()
        except Exception as e:
            print(f"   ❌ Fout bij laden {csv_file}: {e}\n")
    else:
        print(f"   ⚠️  {csv_file} niet gevonden\n")

print(f"📊 TOTAAL ROOT CSV's: {total_root_rows} rijen\n")

# 2. Check odds-portal-scraper CSV's
print("-"*80)
print("\n📊 ODDS-PORTAL-SCRAPER CSV FILES:\n")

odds_portal_dir = "odds-portal-scraper"
scraper_csvs = [
    "odds_20251013_183531.csv",
    "odds_20251013_184113.csv",
    "odds_20251013_190247.csv"
]

total_scraper_rows = 0
for csv_file in scraper_csvs:
    filepath = os.path.join(odds_portal_dir, csv_file)
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            print(f"   {csv_file}:")
            print(f"      Rijen: {len(df)}")
            print(f"      Kolommen: {list(df.columns)[:8]}")
            
            # Check op Nederlandse teams
            if 'home_team' in df.columns or 'Home' in df.columns:
                home_col = 'home_team' if 'home_team' in df.columns else 'Home'
                print(f"      Sample teams: {df[home_col].head(3).tolist()}")
            
            total_scraper_rows += len(df)
            print()
        except Exception as e:
            print(f"   ❌ Fout bij laden {csv_file}: {e}\n")
    else:
        print(f"   ⚠️  {csv_file} niet gevonden\n")

print(f"📊 TOTAAL SCRAPER CSV's: {total_scraper_rows} rijen\n")

# 3. Check data directory
print("-"*80)
print("\n📊 DATA DIRECTORY CSV FILES:\n")

data_dir = "data"
if os.path.exists(data_dir):
    data_csvs = glob(os.path.join(data_dir, "*.csv"))
    
    total_data_rows = 0
    for csv_file in data_csvs[:10]:  # Max 10 om output beperkt te houden
        try:
            df = pd.read_csv(csv_file)
            basename = os.path.basename(csv_file)
            print(f"   {basename}:")
            print(f"      Rijen: {len(df)}")
            total_data_rows += len(df)
        except Exception as e:
            print(f"   ❌ Fout: {e}")
    
    if len(data_csvs) > 10:
        print(f"\n   ... en {len(data_csvs) - 10} andere CSV files")
    
    print(f"\n📊 TOTAAL DATA CSV's: {total_data_rows} rijen (sample van max 10 files)\n")
else:
    print("   ⚠️  Data directory niet gevonden\n")

# 4. TOTAAL OVERZICHT
print("="*80)
print("🎯 TOTAAL OVERZICHT CSV DATA")
print("="*80)
print(f"   Root CSV's:            {total_root_rows} rijen")
print(f"   Scraper CSV's:         {total_scraper_rows} rijen")
print(f"   Huidige training data: 1756 wedstrijden")
print()
print(f"🔥 POTENTIËLE EXTRA ODDS DATA: {total_root_rows + total_scraper_rows} rijen!")
print("="*80 + "\n")
