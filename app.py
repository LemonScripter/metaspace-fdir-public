from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
import traceback
from datetime import datetime

# --- PATH & IMPORT CONFIGURATION ---
base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, 'backend')
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

# Biztonságos importálás a modulokhoz
try:
    from backend.modules.v3_neural_core import NeuralFractalNetwork
    from backend.modules.simulator import SimulationEngine
    from backend.modules.secure_bridge import SecureBridge
except ImportError:
    from modules.v3_neural_core import NeuralFractalNetwork
    from modules.simulator import SimulationEngine
    from modules.secure_bridge import SecureBridge

app = Flask(__name__)
CORS(app)

# --- SECURE BRIDGE INICIALIZÁLÁS (Titkosítás) ---
print("[APP] Initializing Secure Bridge...")
key_path = os.path.join(base_dir, "metaspace_master.key")
if os.path.exists(key_path):
    if SecureBridge.initialize(key_path):
        print("[APP] [OK] Secure Bridge initialized successfully!")
    else:
        print("[APP] [WARNING] Secure Bridge initialization failed (non-critical, continuing without encrypted modules)")
else:
    print(f"[APP] [WARNING] Master key not found at {key_path} (non-critical, continuing without encrypted modules)")

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

@app.route('/api/v3/reset', methods=['POST'])
def v3_reset_api():
    """Backend állapot reset-elése (hard refresh után)"""
    try:
        v3_network.reset_constellation()
        return jsonify({"status": "success", "message": "Network reset successful"})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v3/state', methods=['GET'])
def v3_state_api():
    """Backend állapot lekérése (inicializáláskor)"""
    try:
        active_nodes = [n for n in v3_network.nodes if n.health > 0]
        result = v3_network._evaluate_feasibility(active_nodes, [])
        result["nodes"] = [n.get_telemetry() for n in v3_network.nodes]
        return jsonify({"status": "success", "data": result})
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
        # Opcionális auto_validate flag (alapértelmezett: False - backward compatible)
        auto_validate = data.get('auto_validate', False)
        sim_id = simulator.run(
            data.get('scenario', 'nominal'), 
            int(data.get('duration', 60)),
            auto_validate=auto_validate
        )
        results = simulator.get_results(sim_id)
        return jsonify({"status": "success", "sim_id": sim_id, "data": results})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v3/config', methods=['POST'])
def v3_config_api():
    try:
        data = request.json
        v3_network.set_regen_rate(data.get('regen_rate', 8.5))
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/v3/validation/report/latest', methods=['GET'])
def get_latest_v3_validation_report():
    """Legutóbbi V3 validációs jelentés letöltése"""
    try:
        report = v3_network.get_latest_validation_report()
        if report:
            return jsonify({
                "status": "success",
                "report": report
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No validation report available yet"
            }), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "online",
        "v3_active": v3_network is not None,
        "v2_active": simulator is not None
    })

# --- VALIDÁCIÓS API ---
@app.route('/api/validation/run', methods=['POST'])
def run_validation():
    """Futtatja a validációs teszteket és generál jegyzőkönyvet"""
    try:
        from backend.modules.validation_runner import run_validation
        report = run_validation()
        return jsonify({
            "status": "success",
            "report": report
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/validation/reports', methods=['GET'])
def list_validation_reports():
    """Listázza a validációs jegyzőkönyveket"""
    try:
        import glob
        reports_dir = os.path.join(base_dir, "validation_reports")
        if not os.path.exists(reports_dir):
            return jsonify({"status": "success", "reports": []})
        
        reports = []
        for report_file in glob.glob(os.path.join(reports_dir, "validation_report_*.json")):
            filename = os.path.basename(report_file)
            mtime = os.path.getmtime(report_file)
            reports.append({
                "filename": filename,
                "path": report_file,
                "modified": datetime.fromtimestamp(mtime).isoformat()
            })
        
        # Legfrissebb előre
        reports.sort(key=lambda x: x['modified'], reverse=True)
        
        return jsonify({
            "status": "success",
            "reports": reports
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/validation/reports/<filename>', methods=['GET'])
def get_validation_report(filename):
    """Visszaadja egy validációs jegyzőkönyv tartalmát"""
    try:
        reports_dir = os.path.join(base_dir, "validation_reports")
        report_path = os.path.join(reports_dir, filename)
        
        if not os.path.exists(report_path):
            return jsonify({
                "status": "error",
                "message": "Report not found"
            }), 404
        
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        return jsonify({
            "status": "success",
            "report": report
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)