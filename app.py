from flask import Flask, render_template, jsonify, request, send_from_directory
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

# --- GLOBÁLIS SZIMULÁCIÓ OBJEKTUMOK (csak navigation-plan szimulációhoz) ---
# Fontos: Csak a navigation-plan szimulációhoz használjuk, ne érintse a v3_fractal_sim-et!
_navigation_plan_ekf_simulator = None
_navigation_plan_v3_network = None
_navigation_plan_landsat_model = None

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

# --- CERTIFICATION BUNDLE ROUTE ---
@app.route('/certification')
def certification_index():
    """Serves the main Certification Bundle HTML"""
    return send_from_directory('FINAL_AUDIT_PACKAGE/docs/html', 'MetaSpace_Certification_Bundle.html')

@app.route('/certification/<path:filename>')
def serve_certification_file(filename):
    """Serves other files from the certification package"""
    # Allow serving HTML from docs/html and other assets if needed
    # We might need to serve markdown or json if linked relatively
    # But for now, let's serve from docs/html primarily
    return send_from_directory('FINAL_AUDIT_PACKAGE/docs/html', filename)

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
    try:
        # Simulator inicializálása, ha még nincs
        global simulator
        if not simulator:
            try:
                simulator = SimulationEngine()
                print("[API] Simulator initialized on demand")
            except Exception as init_error:
                print(f"[API] Error initializing simulator: {init_error}")
                traceback.print_exc()
                return jsonify({"status": "error", "message": f"Simulator initialization failed: {str(init_error)}"}), 500
        
        if not simulator:
            return jsonify({"status": "error", "message": "Simulator core offline."}), 500
        
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400
        
        # Opcionális auto_validate flag (alapértelmezett: False - backward compatible)
        auto_validate = data.get('auto_validate', False)
        scenario = data.get('scenario', 'nominal')
        duration = int(data.get('duration', 60))
        
        print(f"[API] Running simulation: scenario={scenario}, duration={duration}, auto_validate={auto_validate}")
        
        sim_id = simulator.run(
            scenario, 
            duration,
            auto_validate=auto_validate
        )
        results = simulator.get_results(sim_id)
        
        print(f"[API] Simulation completed: sim_id={sim_id}, results keys={list(results.keys()) if results else 'None'}")
        
        if not results:
            print(f"[API] WARNING: No results found for sim_id={sim_id}")
            return jsonify({"status": "error", "message": "Simulation completed but no results found. Check server logs."}), 500
        
        return jsonify({"status": "success", "sim_id": sim_id, "data": results})
    except Exception as e:
        print(f"[API] Error in run_simulation: {e}")
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

# --- NAVIGATION PLAN API ---
@app.route('/navigation-plan')
def navigation_plan():
    """Navigációs terv végrehajtás oldal"""
    return render_template('navigation-plan.html')

@app.route('/api/navigation/plan/<plan_id>', methods=['GET'])
def get_navigation_plan(plan_id):
    """Navigációs terv betöltése"""
    try:
        from backend.modules.navigation_plan import NavigationPlan
        
        # Alapértelmezett terv létrehozása (ha nincs fájl)
        if plan_id == 'default':
            plan = NavigationPlan.create_sample_plan()
        else:
            # Fájlból betöltés (ha van)
            plan_path = os.path.join(base_dir, 'backend', 'navigation_plans', f'{plan_id}.json')
            if os.path.exists(plan_path):
                plan = NavigationPlan.load_from_file(plan_path)
            else:
                plan = NavigationPlan.create_sample_plan()
        
        return jsonify({
            "status": "success",
            "plan": {
                "mission_day": plan.mission_day,
                "date": plan.date,
                "orbits": plan.orbits,
                "downlink_windows": plan.downlink_windows,
                "orbital_period_minutes": plan.orbital_period_minutes,
                "orbital_altitude_km": plan.orbital_altitude_km,
                "orbits_per_day": plan.orbits_per_day
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/navigation/current-orbit', methods=['GET'])
def get_current_orbit():
    """Jelenlegi orbit lekérése"""
    try:
        from backend.modules.navigation_plan import NavigationPlan
        import datetime
        
        plan = NavigationPlan.create_sample_plan()
        current_time = request.args.get('time')
        
        if not current_time:
            # Jelenlegi idő
            now = datetime.datetime.now()
            current_time = now.strftime('%H:%M:%S')
        
        orbit = plan.get_current_orbit(current_time)
        
        return jsonify({
            "status": "success",
            "orbit": orbit,
            "current_time": current_time
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/navigation/upcoming-tasks', methods=['GET'])
def get_upcoming_tasks():
    """Közelgő task-ok lekérése"""
    try:
        from backend.modules.navigation_plan import NavigationPlan
        import datetime
        
        plan = NavigationPlan.create_sample_plan()
        lookahead = int(request.args.get('lookahead', 60))
        current_time = request.args.get('time')
        
        if not current_time:
            now = datetime.datetime.now()
            current_time = now.strftime('%H:%M:%S')
        
        tasks = plan.get_upcoming_tasks(current_time, lookahead)
        
        return jsonify({
            "status": "success",
            "tasks": tasks,
            "count": len(tasks)
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/navigation/orbit-parameters', methods=['GET'])
def get_orbit_parameters():
    """Orbit paraméterek lekérése"""
    try:
        from backend.modules.navigation_plan import NavigationPlan
        
        plan = NavigationPlan.create_sample_plan()
        
        return jsonify({
            "status": "success",
            "parameters": {
                "orbital_period_minutes": plan.orbital_period_minutes,
                "orbital_altitude_km": plan.orbital_altitude_km,
                "orbits_per_day": plan.orbits_per_day,
                "inclination_degrees": 98.2  # Landsat-9 spec
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- BIO-CODE FILES API ---
@app.route('/api/biocode/files/latest', methods=['GET'])
def get_latest_biocode_files():
    """Legutóbbi bio-code fájlok lekérése"""
    try:
        from backend.modules.biocode_file_manager import BioCodeFileManager
        
        manager = BioCodeFileManager()
        mission_day = request.args.get('mission_day')
        mission_day = int(mission_day) if mission_day else None
        
        files = manager.get_latest_biocode_files(mission_day)
        
        return jsonify({
            "status": "success",
            "file_paths": files
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/biocode/files/load', methods=['GET'])
def load_biocode_file():
    """Bio-code fájl betöltése"""
    try:
        from backend.modules.biocode_file_manager import BioCodeFileManager
        
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({"status": "error", "message": "Path parameter required"}), 400
        
        manager = BioCodeFileManager()
        
        # Fájl típus meghatározása és betöltés
        # A fájl elérési út alapján meghatározzuk a másik két fájl elérési útját
        if 'level1' in file_path:
            # Level 1 fájl betöltése - szükségünk van a level2 és level3 fájlokra is
            level2_path = file_path.replace('level1', 'level2')
            level3_path = file_path.replace('level1', 'level3')
            try:
                data = manager.load_biocode_files(file_path, level2_path, level3_path)
                return jsonify({"status": "success", "data": data.get("level1", {})})
            except Exception as e:
                print(f"[API] Error loading bio-code files: {e}")
                traceback.print_exc()
                return jsonify({"status": "error", "message": str(e)}), 500
        elif 'level2' in file_path:
            level1_path = file_path.replace('level2', 'level1')
            level3_path = file_path.replace('level2', 'level3')
            try:
                data = manager.load_biocode_files(level1_path, file_path, level3_path)
                return jsonify({"status": "success", "data": data.get("level2", {})})
            except Exception as e:
                print(f"[API] Error loading bio-code files: {e}")
                traceback.print_exc()
                return jsonify({"status": "error", "message": str(e)}), 500
        elif 'level3' in file_path:
            level1_path = file_path.replace('level3', 'level1')
            level2_path = file_path.replace('level3', 'level2')
            try:
                data = manager.load_biocode_files(level1_path, level2_path, file_path)
                return jsonify({"status": "success", "data": data.get("level3", {})})
            except Exception as e:
                print(f"[API] Error loading bio-code files: {e}")
                traceback.print_exc()
                return jsonify({"status": "error", "message": str(e)}), 500
        else:
            return jsonify({"status": "error", "message": "Invalid file path"}), 400
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- EKF FILES API ---
@app.route('/api/ekf/files/latest', methods=['GET'])
def get_latest_ekf_files():
    """Legutóbbi EKF fájlok lekérése"""
    try:
        from backend.modules.ekf_file_manager import EKFFileManager
        
        manager = EKFFileManager()
        mission_day = request.args.get('mission_day')
        mission_day = int(mission_day) if mission_day else None
        
        files = manager.get_latest_ekf_files(mission_day)
        
        return jsonify({
            "status": "success",
            "file_paths": files
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/ekf/files/load', methods=['GET'])
def load_ekf_file():
    """EKF fájl betöltése"""
    try:
        from backend.modules.ekf_file_manager import EKFFileManager
        
        file_path = request.args.get('path')
        if not file_path:
            return jsonify({"status": "error", "message": "Path parameter required"}), 400
        
        manager = EKFFileManager()
        
        # Fájl típus meghatározása
        # Fontos: a fájl elérési utakban lehet backslash (Windows) vagy forward slash
        # A replace() művelet csak az első előfordulást cseréli, ezért biztosítani kell, hogy a helyes részt cseréljük
        try:
            if 'level1' in file_path:
                # Level 1 fájl betöltése - szükségünk van a level2 és level3 fájlokra is
                level2_path = file_path.replace('level1', 'level2', 1)  # Csak az első előfordulást cseréljük
                level3_path = file_path.replace('level1', 'level3', 1)
                data = manager.load_ekf_files(file_path, level2_path, level3_path)
                return jsonify({"status": "success", "data": data.get("level1", {})})
            elif 'level2' in file_path:
                level1_path = file_path.replace('level2', 'level1', 1)  # Csak az első előfordulást cseréljük
                level3_path = file_path.replace('level2', 'level3', 1)
                data = manager.load_ekf_files(level1_path, file_path, level3_path)
                return jsonify({"status": "success", "data": data.get("level2", {})})
            elif 'level3' in file_path:
                level1_path = file_path.replace('level3', 'level1', 1)  # Csak az első előfordulást cseréljük
                level2_path = file_path.replace('level3', 'level2', 1)
                data = manager.load_ekf_files(level1_path, level2_path, file_path)
                return jsonify({"status": "success", "data": data.get("level3", {})})
            else:
                return jsonify({"status": "error", "message": "Invalid file path"}), 400
        except Exception as e:
            print(f"[API] Error loading EKF files: {e}")
            traceback.print_exc()
            return jsonify({"status": "error", "message": str(e)}), 500
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- COMPARISON API ---
@app.route('/api/comparison/metrics', methods=['GET'])
def get_comparison_metrics():
    """EKF vs MetaSpace összehasonlítási metrikák"""
    try:
        from backend.modules.biocode_file_manager import BioCodeFileManager
        from backend.modules.ekf_file_manager import EKFFileManager
        
        mission_day = request.args.get('mission_day')
        mission_day = int(mission_day) if mission_day else None
        
        # Bio-code fájlok
        bio_manager = BioCodeFileManager()
        bio_files = bio_manager.get_latest_biocode_files(mission_day)
        
        # EKF fájlok
        ekf_manager = EKFFileManager()
        ekf_files = ekf_manager.get_latest_ekf_files(mission_day)
        
        # Adatok betöltése
        ekf_data = {}
        metaspace_data = {}
        
        if ekf_files.get('level3'):
            try:
                level1_path = ekf_files.get('level1', '').replace('level3', 'level1')
                level2_path = ekf_files.get('level2', '').replace('level3', 'level2')
                ekf_all = ekf_manager.load_ekf_files(level1_path, level2_path, ekf_files['level3'])
                ekf_data = ekf_all.get('level3', {})
            except:
                pass
        
        if bio_files.get('level3'):
            try:
                level1_path = bio_files.get('level1', '')
                level2_path = bio_files.get('level2', '')
                level3_path = bio_files.get('level3', '')
                
                # Ha a path-ok nem teljesek, próbáljuk kiegészíteni
                if not level1_path and level3_path:
                    level1_path = level3_path.replace('level3', 'level1')
                if not level2_path and level3_path:
                    level2_path = level3_path.replace('level3', 'level2')
                
                bio_all = bio_manager.load_biocode_files(level1_path, level2_path, level3_path)
                level3_data = bio_all.get('level3', {})
                metaspace_data = {
                    "feasibility": level3_data.get('feasibility', 100.0),
                    "action": level3_data.get('action', 'UNKNOWN'),
                    "safety_margin": level3_data.get('safety_margin', 0),
                    "biocode_level3": level3_data.get('biocode', 'N/A')
                }
            except Exception as e:
                print(f"[API] Warning: Could not load bio-code data: {e}")
                traceback.print_exc()
        
        return jsonify({
            "status": "success",
            "ekf": ekf_data,
            "metaspace": metaspace_data
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# --- SIMULATION CONTROL API ---
@app.route('/api/simulation/generate-files', methods=['POST'])
def generate_simulation_files():
    """Új bio-code és EKF fájlok generálása adott mission day-hez"""
    try:
        from backend.modules.v3_neural_core import NeuralFractalNetwork
        from backend.modules.ekf_model import EKFSimulator
        from backend.modules.landsat9 import Landsat9Model
        
        data = request.get_json() or {}
        mission_day = data.get('mission_day', 0)
        
        print(f"[API] Generating files for mission day {mission_day}...")
        
        # VALÓS SZIMULÁCIÓ: Globális objektumok megőrzése (csak navigation-plan szimulációhoz)
        # Fontos: Ezek a változók CSAK a navigation-plan szimulációhoz tartoznak,
        # ne érintsék a v3_fractal_sim vagy más meglévő szimulációkat!
        global _navigation_plan_landsat_model, _navigation_plan_v3_network, _navigation_plan_ekf_simulator
        
        # Landsat9Model inicializálása vagy újrafelhasználása
        if _navigation_plan_landsat_model is None:
            _navigation_plan_landsat_model = Landsat9Model()
        landsat_model = _navigation_plan_landsat_model
        
        # Fizikai szimuláció futtatása (hogy a komponensek frissüljenek)
        # Mission day alapján számított idő (napok → perc)
        time_minutes = mission_day * 24 * 60  # Napok → perc
        # Rövid szimulációs lépés (0.1 perc) a komponensek frissítéséhez
        landsat_model.simulate_step(0.1, current_failure=None)
        
        # MetaSpace bio-code fájlok generálása (VALÓS Landsat9Model-lel)
        if _navigation_plan_v3_network is None:
            _navigation_plan_v3_network = NeuralFractalNetwork(landsat_model=landsat_model)
        v3_network = _navigation_plan_v3_network
        v3_network.mission_day = mission_day
        # Bio-code generálás (process_regeneration hívása) - VALÓS komponens health-tel
        v3_network.process_regeneration()
        
        # EKF fájlok generálása (UGYANAZZAL a Landsat9Model-lel, MEGŐRZÖTT objektum)
        if _navigation_plan_ekf_simulator is None:
            _navigation_plan_ekf_simulator = EKFSimulator(landsat_model)
        ekf_simulator = _navigation_plan_ekf_simulator
        ekf_simulator.mission_day = mission_day
        ekf_simulator.update()  # EKF frissítés (confidence NEM resetelődik!)
        ekf_result = ekf_simulator.save_ekf_execution_files(mission_day=mission_day)
        
        # Bio-code fájlok elérési útjai
        biocode_files = {}
        if hasattr(v3_network, 'biocode_file_manager'):
            try:
                biocode_files = v3_network.biocode_file_manager.get_latest_biocode_files(mission_day)
            except Exception as e:
                print(f"[API] Warning: Could not get bio-code files: {e}")
        
        return jsonify({
            "status": "success",
            "mission_day": mission_day,
            "biocode_files": biocode_files,
            "ekf_files": ekf_result.get("file_paths", {}) if ekf_result else {}
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)