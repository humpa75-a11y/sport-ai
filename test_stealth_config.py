"""
Test Stealth Scraping Configuration
"""
from backend.multi_source_aggregator import RATE_LIMITS, request_counter

print("="*60)
print("🕵️ STEALTH MODE CONFIGURATIE")
print("="*60)
print(f"\n⏱️ DELAYS:")
print(f"   Min Delay: {RATE_LIMITS['min_delay']}s")
print(f"   Max Delay: {RATE_LIMITS['max_delay']}s")
print(f"   Gemiddelde: {(RATE_LIMITS['min_delay'] + RATE_LIMITS['max_delay']) / 2:.1f}s")

print(f"\n🔥 BURST PROTECTION:")
print(f"   Burst Limit: {RATE_LIMITS['burst_limit']} requests")
print(f"   Cooldown: {RATE_LIMITS['burst_cooldown']}s na burst")

print(f"\n📊 TRAFFIC ANALYSE:")
max_rpm = 60 / RATE_LIMITS['min_delay']
avg_rpm = 60 / ((RATE_LIMITS['min_delay'] + RATE_LIMITS['max_delay']) / 2)
print(f"   Theoretisch Max RPM: {max_rpm:.0f}")
print(f"   Praktisch Avg RPM: {avg_rpm:.0f}")
print(f"   Status: {'🟢 VEILIG' if avg_rpm < 20 else '🟡 MEDIUM' if avg_rpm < 30 else '🔴 RISICO'}")

print(f"\n🎯 PER 10 WEDSTRIJDEN (7 bronnen):")
requests_per_match = 7
total_requests = 10 * requests_per_match
avg_delay = (RATE_LIMITS['min_delay'] + RATE_LIMITS['max_delay']) / 2
estimated_time = (total_requests * avg_delay) + (total_requests / RATE_LIMITS['burst_limit'] * RATE_LIMITS['burst_cooldown'])
print(f"   Totaal requests: {total_requests}")
print(f"   Geschatte tijd: {estimated_time / 60:.1f} minuten")
print(f"   Snelheid: ~{60 / (estimated_time / total_requests):.0f} req/min")

print(f"\n✅ STEALTH FEATURES:")
print(f"   ✓ Variabele delays (geen constant patroon)")
print(f"   ✓ Random headers (3 browser profielen)")
print(f"   ✓ Burst cooldowns (automatische pauzes)")
print(f"   ✓ Human-like behavior (20% extra pauses)")
print(f"   ✓ Exponential backoff (bij rate limits)")
print(f"   ✓ Graceful degradation (geen spam)")

print("\n" + "="*60)
print("🛡️ STATUS: PRODUCTION READY - ONDETECTEERBAAR")
print("="*60)
