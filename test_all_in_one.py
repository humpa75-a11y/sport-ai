"""
🔥 ALL-IN-ONE: Start server EN test Eerste Divisie! 🔥
"""
import subprocess
import time
import requests
import sys

print("\n" + "="*80)
print("🚀 ALL-IN-ONE: SERVER + EERSTE DIVISIE TEST")
print("="*80)

# Start server in background
print("\n1️⃣  Starting server...")
server_process = subprocess.Popen(
    [sys.executable, "backend/app.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Wait for server to start
print("   ⏳ Waiting 8 seconds for server startup...")
time.sleep(8)

# Test if server is running
API_URL = "http://127.0.0.1:5000"
try:
    response = requests.get(f"{API_URL}/api/status", timeout=5)
    if response.status_code == 200:
        print("   ✅ Server is RUNNING!")
    else:
        print(f"   ⚠️  Server responded with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Server niet bereikbaar: {e}")
    server_process.kill()
    sys.exit(1)

# Now test Eerste Divisie!
print("\n2️⃣  Testing EERSTE DIVISIE predictions...")
print("="*80)

test_matches = [
    ('FC Eindhoven', 'Helmond Sport', 'Brabantse Derby 🔥'),
    ('ADO Den Haag', 'FC Volendam', 'Top Teams 👊'),
    ('De Graafschap', 'Roda JC', 'Traditie ⚔️'),
    ('NAC Breda', 'Cambuur', 'Degradanten 🏆'),
]

results = []

for home, away, desc in test_matches:
    print(f"\n📊 {desc}: {home} vs {away}")
    print("-" * 80)
    
    payload = {'home_team': home, 'away_team': away, 'speelronde': 15}
    
    try:
        response = requests.post(f"{API_URL}/api/predict", json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            pred = result['prediction']
            
            print(f"   ✅ Score: {pred.get('predicted_score', 'N/B')}")
            print(f"      Goals: {pred.get('expected_home_goals', 0):.2f} - {pred.get('expected_away_goals', 0):.2f}")
            print(f"      Confidence: {pred.get('confidence_factor', 0):.1f}%")
            
            results.append({
                'match': f"{home} vs {away}",
                'score': pred.get('predicted_score', 'N/B'),
                'confidence': pred.get('confidence_factor', 0)
            })
        else:
            print(f"   ❌ Error {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Fout: {e}")

# Summary
print("\n" + "="*80)
print("📊 RESULTATEN")
print("="*80)

if results:
    for r in results:
        print(f"   {r['match']}: {r['score']} ({r['confidence']:.1f}%)")
    
    avg_conf = sum(r['confidence'] for r in results) / len(results)
    print(f"\n   Gemiddelde Confidence: {avg_conf:.1f}%")
    print(f"\n🏆 {len(results)} SUCCESVOLLE VOORSPELLINGEN!")
    print("   EERSTE DIVISIE = KEI HARD GESLAGEN! 💪")
else:
    print("   ❌ Geen succesvolle voorspellingen")

print("="*80)

# Kill server
print("\n3️⃣  Stopping server...")
server_process.kill()
print("   ✅ Server gestopt")
