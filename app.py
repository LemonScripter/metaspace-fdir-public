from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
import traceback

# --- PATH CONFIGURATION ---
# Meghatározzuk a pontos elérési utakat, hogy a Railway biztosan megtalálja a fájlokat
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, 'backend')

# Hozzáadjuk a rendszer útvonalakhoz a backend mappát
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

print(f"[SYSTEM] Base Dir: {base_dir}")
print(f"[SYSTEM] Backend Dir: {backend_dir}")

# --- MODULE IMPORT ---
# Biztonságos importálás hibakezeléssel
try:
    from modules.simulator import SimulationEngine
    print("[SYSTEM] SUCCESS: Imported SimulationEngine from 'modules.simulator'")
except ImportError as e:
    print(f"[SYSTEM WARNING] Standard import failed: {e}")
    print("[SYSTEM] Attempting fallback import...")
    try:
        # Ha az első nem sikerül, megpróbáljuk teljes útvonallal
        from backend.modules.simulator import SimulationEngine
        print("[SYSTEM] SUCCESS: Imported SimulationEngine from 'backend.modules.simulator'")
    except ImportError as e2:
        print(f"[SYSTEM CRITICAL] Failed to import SimulationEngine: {e2}")
        # Itt nem állítjuk le, de a simulator változó None lesz, amit később kezelünk
        SimulationEngine = None

app = Flask(__name__)
CORS(app)

# --- INICIALIZÁLÁS ---
print("--- METASPACE SERVER STARTUP (v2.0) ---")

simulator = None
if SimulationEngine:
    try:
        simulator = SimulationEngine()
        print("[SYSTEM] Simulation Core v2.0 Online.")
    except Exception as e:
        print(f"[SYSTEM CRITICAL] Error initializing SimulationEngine: {e}")
        traceback.print_exc()
else:
    print("[SYSTEM CRITICAL] SimulationEngine class is missing!")


@app.route('/')
def index():
    """A fő Dashboard betöltése"""
    return render_template('index.html')


@app.route('/about')
def about():
    """Az About oldal betöltése"""
    return render_template('about.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Egyszerű ellenőrzés, hogy fut-e a szerver"""
    status = "online" if simulator else "degraded (simulator missing)"
    return jsonify({
        "status": status, 
        "system": "MetaSpace Simulator v2.0",
        "backend_path": backend_dir
    })


@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    """
    Indít egy szimulációt a kért paraméterekkel.
    JSON Body: { "scenario": "gps_antenna", "duration": 60 }
    """
    if not simulator:
        return jsonify({"status": "error", "message": "Simulator core is not initialized."}), 500

    try:
        data = request.json
        # Biztonságos adatkinyerés alapértelmezett értékekkel
        scenario = data.get('scenario', 'nominal')
        # Fontos: int-re kasztoljuk, mert a JSON stringként küldheti
        duration = int(data.get('duration', 60))
        
        print(f"[API] Simulation Request: Scenario='{scenario}', Duration={duration} days")
        
        # 1. Szimuláció futtatása (visszaad egy UUID-t)
        sim_id = simulator.run(scenario, duration)
        
        # 2. Azonnali eredmény lekérés (mivel a frontend várja a grafikont)
        results = simulator.get_results(sim_id)
        
        if not results:
            print(f"[API ERROR] No results found for ID: {sim_id}")
            return jsonify({"status": "error", "message": "Simulation finished but produced no data."}), 500
        
        return jsonify({
            "status": "success",
            "sim_id": sim_id,
            "data": results
        })
        
    except Exception as e:
        print(f"[API CRITICAL ERROR] Exception during simulation: {str(e)}")
        traceback.print_exc() # Kiírja a teljes hibaüzenetet a logba
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    # A portot a környezeti változóból olvassuk (Railway miatt fontos!)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)