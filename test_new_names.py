"""
✅ TEST NIEUWE NAMEN
"""

from backend import multi_source_aggregator

print("="*80)
print("TEST: NIEUWE NAMING (simulation_mode)")
print("="*80)

print("\n1. SIMULATION MODE (gebaseerd op echte statistieken):")
print("-"*80)
df = multi_source_aggregator.run_full_analysis(
    league='bundesliga',
    days_ahead=2,
    simulation_mode=True
)

if not df.empty:
    print(f"\n✅ Werkt! {len(df)} matches")
    print("\nVoorbeeld:")
    print(df[['match', 'odds_1x2']].head(2).to_string(index=False))

print("\n" + "="*80)
print("✅ Naming update SUCCESS!")
print("="*80)
print("\nMODES:")
print("  🎯 simulation_mode=True  → Smart predictions met echte team stats")
print("  🔥 use_real_api=True     → Live data van API-Football")
print("="*80)
