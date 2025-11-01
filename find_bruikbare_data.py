#!/usr/bin/env python3
"""
🎯 BRUIKBARE TRAININGSDATA EXTRACTOR 🎯
Zoekt naar CSV's met daadwerkelijke match resultaten (scores)
"""

import os
import pandas as pd
from glob import glob

print("\n" + "="*80)
print("🎯 ZOEKEN NAAR BRUIKBARE TRAININGSDATA (MET SCORES)")
print("="*80 + "\n")

def check_csv_for_results(filepath):
    """Check of een CSV wedstrijdresultaten bevat"""
    try:
        df = pd.read_csv(filepath)
        
        # Zoek naar score kolommen
        score_columns = []
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['score', 'goals', 'result', 'final', 'ft']):
                score_columns.append(col)
        
        # Check of we home/away goals hebben
        has_home_goals = any('home' in col.lower() and ('goal' in col.lower() or 'score' in col.lower()) 
                            for col in df.columns)
        has_away_goals = any('away' in col.lower() and ('goal' in col.lower() or 'score' in col.lower()) 
                            for col in df.columns)
        
        if score_columns or (has_home_goals and has_away_goals):
            return True, len(df), score_columns, df.columns.tolist()
        
        return False, 0, [], []
        
    except Exception as e:
        return False, 0, [], []

# Check alle directories
directories = [
    ".",
    "data",
    "odds-portal-scraper"
]

bruikbare_files = []
totaal_bruikbare_matches = 0

print("🔍 SCANNEN VAN ALLE CSV BESTANDEN...\n")

for directory in directories:
    if not os.path.exists(directory):
        continue
    
    # Vind alle CSV's
    if directory == ".":
        csvs = [f for f in os.listdir(".") if f.endswith(".csv")]
    else:
        csvs = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".csv")]
    
    for csv_path in csvs:
        has_results, num_rows, score_cols, all_cols = check_csv_for_results(csv_path)
        
        if has_results:
            print(f"✅ GEVONDEN: {csv_path}")
            print(f"   Rijen: {num_rows}")
            print(f"   Score kolommen: {score_cols}")
            print(f"   Alle kolommen: {all_cols[:10]}...")
            print()
            
            bruikbare_files.append({
                'path': csv_path,
                'rows': num_rows,
                'score_cols': score_cols
            })
            totaal_bruikbare_matches += num_rows

print("="*80)
print("📊 RESULTATEN")
print("="*80)
print(f"✅ Bruikbare CSV's gevonden: {len(bruikbare_files)}")
print(f"🎯 Totaal matches met scores: {totaal_bruikbare_matches}")
print(f"📈 Huidige training data: 1756 matches")

if totaal_bruikbare_matches > 0:
    print(f"\n🔥 POTENTIEEL NIEUWE TOTAAL: {1756 + totaal_bruikbare_matches} matches!")
    print("\n📋 BRUIKBARE BESTANDEN:")
    for file in bruikbare_files:
        print(f"   - {file['path']}: {file['rows']} matches")
else:
    print("\n⚠️  Geen extra bruikbare trainingsdata gevonden met scores")
    print("   De CSV's bevatten vooral bookmaker odds, geen historische resultaten")

print("="*80 + "\n")

# Check ook de data folder voor andere formats
print("🔍 EXTRA CHECK: JSON BESTANDEN IN DATA FOLDER\n")

data_jsons = glob("data/*.json")
for json_file in data_jsons[:5]:
    try:
        import json
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structuur
        if isinstance(data, list) and len(data) > 0:
            sample = data[0]
            has_scores = any(key in sample for key in ['home_goals', 'away_goals', 'score', 'goals'])
            
            if has_scores:
                print(f"✅ {os.path.basename(json_file)}: {len(data)} matches (HAS SCORES!)")
            else:
                print(f"   {os.path.basename(json_file)}: {len(data)} items (geen scores)")
        elif isinstance(data, dict):
            print(f"   {os.path.basename(json_file)}: Dictionary met {len(data)} keys")
    except:
        pass

print()
