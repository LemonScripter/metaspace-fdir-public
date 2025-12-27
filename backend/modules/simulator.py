import json
import random
import os
import copy
from datetime import datetime
from .secure_bridge import SecureBridge
from .metaspace import MetaSpaceSimulator
from .landsat9 import Landsat9Model
from .ekf_model import EKFSimulator
from .failure import FailureInjector

class SimulationEngine:
    def __init__(self):
        self.simulations = {}
        self.results = {}
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        key_path = os.path.join(base_dir, "metaspace_master.key")
        
        print(f"[SIMULATOR] Secure Bridge inicializálása: {key_path}")
        if SecureBridge.initialize(key_path):
            print("[SIMULATOR] Secure Bridge ONLINE. Titkos magok aktívak.")
        else:
            print("[SIMULATOR] FIGYELEM: Secure Bridge OFFLINE.")

    def run(self, scenario, duration, seed=None):
        if seed: random.seed(seed)
        sim_id = self._generate_id()
        
        # 1. Modellek
        landsat_metaspace = Landsat9Model()
        landsat_ekf = copy.deepcopy(landsat_metaspace) 
        
        # 2. VÉLETLENSZERŰSÉG GENERÁLÁSA
        # A hiba a futamidő 10%-a és 80%-a között történjen valahol
        min_day = max(2, int(duration * 0.1))
        max_day = max(min_day + 1, int(duration * 0.8))
        random_fail_day = random.randint(min_day, max_day)
        
        # Config
        if isinstance(scenario, str):
            config = {"failure_type": scenario}
        else:
            config = scenario
            
        # Injektorok beállítása a véletlen nappal
        injector_ms = FailureInjector(config)
        injector_ms.set_random_day(random_fail_day)
        
        injector_ekf = FailureInjector(config)
        injector_ekf.set_random_day(random_fail_day)
        
        # 3. Futamok
        print(f"--- MetaSpace futam (Hiba napja: {random_fail_day}) ---")
        ms_results = self._run_simulation_loop(
            landsat_metaspace, injector_ms, duration, use_metaspace=True
        )
        
        print(f"--- EKF futam (Hiba napja: {random_fail_day}) ---")
        ekf_results = self._run_simulation_loop(
            landsat_ekf, injector_ekf, duration, use_metaspace=False
        )
        
        # Eredmény összeállítása
        result_data = {
            'simulation_id': sim_id,
            'scenario': scenario,
            'timestamp': datetime.now().isoformat(),
            'metaspace': ms_results,
            'ekf': ekf_results,
            'failure_day': random_fail_day # Elküldjük a frontendnek is
        }

        # --- ADATMENTÉS (AUDIT) ---
        # A results mappa létrehozása a gyökérkönyvtárban
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        results_dir = os.path.join(root_dir, "results")
        
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            
        # Fájl mentése JSON formátumban
        filename = f"{results_dir}/{sim_id}_{config.get('failure_type', 'unknown')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(result_data, f, indent=4)
            print(f"[SIMULATOR] Eredmények auditálva ide: {filename}")
        except Exception as e:
            print(f"[SIMULATOR] Hiba a mentés során: {e}")

        self.results[sim_id] = result_data
        return sim_id

    def _run_simulation_loop(self, model, injector, duration, use_metaspace):
        metaspace = MetaSpaceSimulator(model) if use_metaspace else None
        ekf = EKFSimulator(model) 
        
        timeline = []
        
        for day in range(duration):
            # 1. Hiba Injektálás (Minden nap ellenőrizzük, el kell-e rontani a hardvert)
            injector.apply_failures(model, day)
            
            # 2. Fizikai Szimuláció (NAPI LÉPÉS - FONTOS VÁLTOZÁS!)
            # step() helyett simulate_day()-t hívunk az energiamérleg miatt
            model.simulate_day() 
            
            # 3. Érzékelés
            ekf.update()
            
            mode = "FULL_MISSION"
            feasibility = 100
            latency = 0
            message = ""
            
            # Állapotok kiolvasása a modellből
            phys_gps_err = getattr(model, 'gps_error', 0.0)
            phys_bat_lvl = getattr(model, 'battery_level', 100.0)
            phys_imu_err = getattr(model, 'imu_accumulated_error', 0.0)

            if use_metaspace:
                # --- METASPACE ---
                metaspace.update()
                feasibility = metaspace.mission_feasibility
                mode = metaspace.execution_mode
                latency = metaspace.detection_latency
                
                if mode == "SAFE_MODE":
                    if phys_bat_lvl < 20.0:
                         message = "KRITIKUS: Energiahiány! Payload lekapcsolva a 'Dead Bus' elkerülése érdekében."
                    elif phys_gps_err > 50.0:
                         message = "KRITIKUS: GPS hiba! Adatgyűjtés blokkolva (Selejt védelem)."
                    elif phys_imu_err > 0.5:
                         message = "KRITIKUS: Navigációs sodródás! Pályakorrekció szükséges."
                    else:
                         message = "BIZTONSÁGI ZÁR: Ismeretlen anomália."
                elif latency > 0 and feasibility < 100:
                    message = "FIGYELEM: MetaSpace korrekció."
                else:
                    message = "Nominális működés (MetaSpace)."
                    
            else:
                # --- EKF ---
                if ekf.anomaly_detected:
                    mode = "SAFE_MODE"
                    feasibility = ekf.confidence
                    message = "HIBA: EKF hibát jelzett (késve)."
                
                # Rejtett hibák (Ez a lényeg!)
                elif phys_bat_lvl < 20.0:
                    message = "VESZÉLY: Kritikus akku! Az EKF nem látja, a műhold elveszhet."
                    feasibility = 100 
                elif phys_gps_err > 50.0:
                    message = "VESZÉLY: GPS hiba! Az EKF selejtet ment."
                    feasibility = 100
                elif phys_imu_err > 1.0:
                    message = "VESZÉLY: Lopakodó drift! Navigáció pontatlan."
                    feasibility = 100
                else:
                    message = "Nominális működés (EKF)."

            timeline.append({
                'day': day,
                'feasibility': feasibility,
                'mode': mode,
                'latency_ms': f"{latency:.2f}",
                'gps_error': f"{phys_gps_err:.2f}",
                'battery_level': f"{phys_bat_lvl:.1f}",
                'imu_error': f"{phys_imu_err:.4f}",
                'message': message
            })
            
        return {'timeline': timeline}

    def get_results(self, sim_id):
        return self.results.get(sim_id)

    def _generate_id(self):
        return f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"