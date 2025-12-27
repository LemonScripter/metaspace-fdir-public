# test_simulation.py
from backend.modules.simulator import SimulationEngine

print("--- TELJES SZIMULÁCIÓ TESZT ---")
sim = SimulationEngine()
sim_id = sim.run("gps_antenna", duration=20)
results = sim.get_results(sim_id)

print("\n--- EREDMÉNYEK ---")
for entry in results['metaspace']['timeline']:
    print(f"Nap {entry['day']}: Feasibility={entry['feasibility']}% Mode={entry['mode']} Latency={entry['latency_ms']}ms")