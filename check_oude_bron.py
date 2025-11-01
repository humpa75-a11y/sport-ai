#!/usr/bin/env python3
"""
🔍 OUDE BRON DATA CHECKER 🔍
Controleert hoeveel wedstrijden er in de odds-portal-scraper map zitten
"""

import json
import os
from collections import Counter

print("\n" + "="*80)
print("🔍 CONTROLEREN OUDE BRON DATA IN ODDS-PORTAL-SCRAPER")
print("="*80 + "\n")

odds_portal_dir = "odds-portal-scraper"

# 1. Check MASTER_DATA files
master_files = [
    "MASTER_DATA_20251013_183531.json",
    "MASTER_DATA_20251013_184113.json", 
    "MASTER_DATA_20251013_190247.json"
]

print("📊 MASTER_DATA FILES:\n")
total_master_matches = 0
all_competitions = Counter()

for file in master_files:
    filepath = os.path.join(odds_portal_dir, file)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check structuur - kan list of dict zijn
            if isinstance(data, list):
                matches = data
            elif isinstance(data, dict):
                matches = data.get('matches', [])
            else:
                matches = []
            
            print(f"   {file}:")
            print(f"      Wedstrijden: {len(matches)}")
            
            # Probeer competities te tellen
            if matches:
                sample = matches[0]
                print(f"      Sample keys: {list(sample.keys())[:10]}")
                
                # Check op competitie velden
                for match in matches:
                    comp = match.get('competition') or match.get('league') or match.get('tournament')
                    if comp:
                        all_competitions[comp] += 1
            
            total_master_matches += len(matches)
            print()
            
        except Exception as e:
            print(f"   ❌ Fout bij laden {file}: {e}\n")
    else:
        print(f"   ⚠️  {file} niet gevonden\n")

print(f"📊 TOTAAL MASTER_DATA: {total_master_matches} wedstrijden")

if all_competitions:
    print(f"\n🏆 COMPETITIES GEVONDEN:")
    for comp, count in all_competitions.most_common(10):
        print(f"   - {comp}: {count} wedstrijden")

# 2. Check AI_TRAINING files
print("\n" + "-"*80)
print("\n📊 AI_TRAINING FILES:\n")

ai_files = [
    "AI_TRAINING_20251013_183531.json",
    "AI_TRAINING_20251013_184113.json",
    "AI_TRAINING_20251013_190247.json"
]

total_ai_matches = 0

for file in ai_files:
    filepath = os.path.join(odds_portal_dir, file)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check structuur
            if isinstance(data, list):
                matches = data
            elif isinstance(data, dict):
                matches = data.get('matches', data.get('training_data', []))
            else:
                matches = []
            
            print(f"   {file}:")
            print(f"      Wedstrijden: {len(matches)}")
            
            if matches:
                sample = matches[0]
                print(f"      Sample keys: {list(sample.keys())[:10]}")
            
            total_ai_matches += len(matches)
            print()
            
        except Exception as e:
            print(f"   ❌ Fout bij laden {file}: {e}\n")
    else:
        print(f"   ⚠️  {file} niet gevonden\n")

print(f"📊 TOTAAL AI_TRAINING: {total_ai_matches} wedstrijden")

# 3. TOTAAL OVERZICHT
print("\n" + "="*80)
print("🎯 TOTAAL OVERZICHT OUDE BRON")
print("="*80)
print(f"   MASTER_DATA files: {total_master_matches} wedstrijden")
print(f"   AI_TRAINING files: {total_ai_matches} wedstrijden")
print(f"   HUIDIGE systeem:   1756 wedstrijden")
print()
print(f"🔥 POTENTIËLE EXTRA DATA: {total_master_matches + total_ai_matches} wedstrijden!")
print(f"🚀 NIEUWE TOTAAL:         {1756 + total_master_matches + total_ai_matches} wedstrijden!")
print("="*80 + "\n")

# 4. Check of data bruikbaar is voor Nederlandse competities
print("🇳🇱 NEDERLANDSE COMPETITIES CHECK:")
nederlandse_competities = [
    'Eredivisie', 'Eerste Divisie', 'Netherlands', 
    'Dutch', 'KNVB', 'Holland'
]

nederlandse_matches = 0
for comp, count in all_competitions.items():
    if any(ned.lower() in comp.lower() for ned in nederlandse_competities):
        print(f"   ✅ {comp}: {count} wedstrijden")
        nederlandse_matches += count

if nederlandse_matches > 0:
    print(f"\n🎯 TOTAAL NEDERLANDSE DATA: {nederlandse_matches} wedstrijden!")
else:
    print(f"\n⚠️  Geen Nederlandse competities gevonden in metadata")
    print(f"   Maar de data kan nog steeds bruikbaar zijn!")

print()
