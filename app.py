from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
import traceback

# --- PATH & IMPORT CONFIGURATION ---
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Biztonságos importálás a modulokhoz
try:
    from backend.modules.v3_neural_core import NeuralFractalNetwork
    from backend.modules.simulator import SimulationEngine
except ImportError:
    from modules.v3_neural_core import NeuralFractalNetwork
    from modules.simulator import SimulationEngine

app = Flask(__name__)
CORS(app)

# --- ENGINE INICIALIZÁLÁS ---
simulator = SimulationEngine() if 'SimulationEngine' in globals() else None
v3_network = NeuralFractalNetwork()

# --- OLDAL ROUTE-OK ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/v3-sandbox')
def v3_sandbox():
    return render_template('v3_fractal_sim.html')

# --- V3 NEURAL API (Regeneráció és Káosz) ---
@app.route('/api/v3/chaos', methods=['POST'])
def v3_chaos_api():
    try:
        data = request.json
        killed_nodes = data.get('killed_nodes', [])
        # Lefuttatja a pusztítást és a Master Migration-t
        results = v3_network.inject_chaos_and_calculate(killed_nodes)
        return jsonify({"status": "success", "data": results})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v3/regen', methods=['POST'])
def v3_regen_api():
    try:
        # Lefuttatja az autonóm öngyógyító ciklust
        regen_results = v3_network.process_regeneration()
        return jsonify({"status": "success", "data": regen_results})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- V2 SIMULATOR API ---
@app.route('/api/simulation', methods=['POST'])
def run_simulation():
    if not simulator:
        return jsonify({"status": "error", "message": "Simulator core offline."}), 500
    try:
        data = request.json
        sim_id = simulator.run(data.get('scenario', 'nominal'), int(data.get('duration', 60)))
        results = simulator.get_results(sim_id)
        return jsonify({"status": "success", "sim_id": sim_id, "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v3/config', methods=['POST'])
def v3_config_api():
    try:
        data = request.json
        v3_network.set_regen_rate(data.get('regen_rate', 8.5))
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "v3_active": v3_network is not None,
        "v2_active": simulator is not None
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)