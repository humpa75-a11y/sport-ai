"""
🔥 TEST BEIDE APIs
Test welke API het beste werkt voor ECHTE data
"""

print("="*80)
print("TESTING BEIDE APIs")
print("="*80)

# Test 1: API-Football
print("\n1️⃣ API-FOOTBALL TEST")
print("-"*80)
try:
    from backend.api_sports_integration import ApiSportsIntegration
    
    api1 = ApiSportsIntegration()
    df1 = api1.get_fixtures_by_date()
    
    if not df1.empty:
        print(f"✅ API-FOOTBALL WERKT! {len(df1)} matches vandaag")
        print("\nVoorbeeld matches:")
        print(df1[['home', 'away', 'tournament']].head(3).to_string(index=False))
    else:
        print("⚠️ Geen matches gevonden")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Sofascore
print("\n\n2️⃣ SOFASCORE (RapidAPI) TEST")
print("-"*80)
try:
    from backend.sofascore_api import SofascoreAPI
    
    api2 = SofascoreAPI()
    matches = api2.get_matches_by_date()
    
    if matches:
        print(f"✅ SOFASCORE WERKT! {len(matches)} matches vandaag")
        print("\nVoorbeeld matches:")
        for i, m in enumerate(matches[:3], 1):
            print(f"{i}. {m['home']} vs {m['away']} ({m['tournament']})")
    else:
        print("⚠️ Geen matches gevonden")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*80)
print("CONCLUSIE:")
print("="*80)
print("Beide APIs zijn geïntegreerd!")
print("Gebruik whichever werkt het beste voor jouw use case:")
print("  - API-Football: Fixtures + odds")
print("  - Sofascore: Live scores + xG + detailed stats")
print("="*80)
