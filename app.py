# app.py
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sys
import os

# Backend modulok importálása
# Mivel a backend mappa almappában van, hozzáadjuk az útvonalhoz
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from modules.simulator import SimulationEngine

app = Flask(__name__)
CORS(app)  # Engedélyezzük a cross-origin kéréseket a fejlesztéshez

# --- INICIALIZÁLÁS ---
print("--- METASPACE SERVER STARTUP ---")
# A szerver indulásakor betöltjük a titkos magot
simulator = SimulationEngine()

@app.route('/')
def index():
    """A fő Dashboard betöltése"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Egyszerű ellenőrzés, hogy fut-e a szerver"""
    return jsonify({"status": "online", "system": "MetaSpace Simulator v1.0"})

@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    """
    Indít egy szimulációt a kért paraméterekkel.
    JSON Body: { "scenario": "gps_antenna", "duration": 365 }
    """
    data = request.json
    scenario = data.get('scenario', 'nominal')
    duration = data.get('duration', 100)
    
    print(f"[API] Simulation request: {scenario} ({duration} days)")
    
    try:
        # A szimuláció futtatása (ez használja a titkos magot)
        sim_id = simulator.run(scenario, duration)
        
        # Az eredmények lekérése
        results = simulator.get_results(sim_id)
        
        return jsonify({
            "status": "success",
            "sim_id": sim_id,
            "data": results
        })
        
    except Exception as e:
        print(f"[API ERROR] {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Debug módban indítjuk, hogy lássuk a hibákat
    app.run(debug=True, host='0.0.0.0', port=5000)