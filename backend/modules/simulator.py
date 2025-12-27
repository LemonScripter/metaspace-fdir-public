import json
import random
import os
import uuid
import time
from datetime import datetime
from .landsat9 import Landsat9Model

# Megpróbáljuk importálni a SecureBridge-et, de nem omlunk össze, ha nincs meg
try:
    from .secure_bridge import SecureBridge
except ImportError:
    SecureBridge = None

class SimulationEngine:
    """
    MetaSpace v2.0 Simulation Engine
    --------------------------------
    Ez a központi vezérlő egység, amely összeköti a Flask API-t 
    a mélyszintű fizikai modellel (Landsat9Model).
    
    Feladatai:
    1. A szimulációs környezet inicializálása (SecureBridge).
    2. A v2.0 Bio-Architektúra példányosítása.
    3. Időbeli léptetés (Time-stepping) és hiba-injektálás vezérlése.
    4. Az eredmények strukturált mentése (Audit Trail).
    """

    def __init__(self):
        self.results_cache = {}
        
        # Könyvtárstruktúra beállítása
        # Visszalépünk a gyökérkönyvtárba (backend/modules -> backend -> root)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.results_dir = os.path.join(self.base_dir, "results")
        
        # Eredménykönyvtár létrehozása, ha nem létezik
        if not os.path.exists(self.results_dir):
            try:
                os.makedirs(self.results_dir)
                print(f"[SIMULATOR] Results directory created at: {self.results_dir}")
            except OSError as e:
                print(f"[SIMULATOR] ERROR creating results directory: {e}")

        # Biztonsági modul inicializálása (Legacy support)
        self._init_security()

    def _init_security(self):
        """
        Ellenőrzi a titkosító kulcsokat és a rendszer integritását.
        """
        print("[SIMULATOR] Initializing System Core...")
        if SecureBridge:
            key_path = os.path.join(self.base_dir, "metaspace_master.key")
            if os.path.exists(key_path):
                print(f"[SIMULATOR] Secure Bridge Found: {key_path}")
                if SecureBridge.initialize(key_path):
                    print("[SIMULATOR] Secure Bridge ONLINE. Invariant Enforcer Active.")
                else:
                    print("[SIMULATOR] WARNING: Secure Bridge Init Failed.")
            else:
                print("[SIMULATOR] NOTICE: Master Key not found. Running in simulation mode.")
        else:
            print("[SIMULATOR] SecureBridge module not present (v2.0 Bypass Active).")

    def run(self, scenario, duration):
        """
        A fő szimulációs ciklus futtatása.
        
        Args:
            scenario (str): A kiválasztott hiba típusa (pl. 'solar_panel').
            duration (int): A szimuláció hossza napokban.
            
        Returns:
            str: A szimuláció egyedi azonosítója (UUID).
        """
        sim_id = str(uuid.uuid4())
        start_time = time.time()
        
        print(f"\n--- MetaSpace v2.0 Simulation Start [ID: {sim_id}] ---")
        print(f"Scenario: {scenario} | Duration: {duration} days")

        # 1. MODEL INICIALIZÁLÁS (Bio-Architektúra)
        # Itt példányosítjuk az új Landsat9Model-t, ami már tartalmazza
        # a Subsystems (EPS, GNC) és Components (Sejt) logikát.
        satellite = Landsat9Model()
        
        # 2. HIBA IDŐZÍTÉS (Randomizálás)
        # A hiba ne azonnal történjen, hanem a futamidő 20%-a és 80%-a között.
        min_day = max(2, int(duration * 0.2))
        max_day = max(min_day + 1, int(duration * 0.8))
        failure_day = random.randint(min_day, max_day)
        
        # Átváltás percekre (mivel a fizikai motor perc alapon számol)
        failure_minute_start = failure_day * 24 * 60
        
        print(f"[SIMULATOR] Stochastic Failure Injection scheduled for Day {failure_day} (T+{failure_minute_start} min)")

        # 3. SZIMULÁCIÓS LOOP
        # Óránkénti mintavételezést használunk a gyors válaszidő érdekében,
        # de a Landsat9Model a háttérben kezeli a fizikai változókat.
        dt_minutes = 60 
        total_minutes = duration * 24 * 60
        
        history = []
        failure_triggered = False
        
        # Végigmegyünk az idővonalon...
        for t in range(0, total_minutes, dt_minutes):
            current_day_float = t / (24 * 60)
            
            # Ellenőrizzük, eljött-e a hiba ideje
            active_failure = None
            if not failure_triggered and t >= failure_minute_start:
                if scenario != 'nominal':
                    active_failure = scenario
                    failure_triggered = True
                    print(f"[SIMULATOR] >> INJECTION TRIGGERED: {scenario} at T+{t}min")

            # --- V2 CORE LOGIC HÍVÁS ---
            # Ez a sor a lelke mindennek: meghívjuk a fizikai modellt.
            # A visszatérő 'telemetry' dictionary tartalmazza az EPS és GNC állapotokat.
            telemetry = satellite.simulate_step(dt_minutes, failure_mode=active_failure)
            
            # Kiegészítjük metaadatokkal a frontend számára
            telemetry['day_float'] = round(current_day_float, 2)
            telemetry['timestamp_min'] = t
            
            # Hozzáadjuk a történelmet
            history.append(telemetry)

        # 4. EREDMÉNY CSOMAG ÖSSZEÁLLÍTÁSA
        execution_time = time.time() - start_time
        print(f"[SIMULATOR] Simulation completed in {execution_time:.4f}s")
        
        result_package = {
            'sim_id': sim_id,
            'timestamp': datetime.now().isoformat(),
            'scenario': scenario,
            'days': duration,
            'failure_day': failure_day,
            'data_points_count': len(history),
            'execution_time_sec': execution_time,
            'model_version': 'v2.0 (Bio-Architecture)',
            # Az utolsó állapotot elküldjük, hogy lássuk, túlélte-e
            'final_status': history[-1],
            # A teljes logot is elmentjük, ha részletes elemzés kell
            'telemetry_log': history 
        }

        # 5. MENTÉS ÉS CACHE
        self._save_results(sim_id, result_package)
        self.results_cache[sim_id] = result_package
        
        return sim_id

    def _save_results(self, sim_id, data):
        """
        Eredmények mentése JSON fájlba a 'results' mappába.
        Ez biztosítja az Audit Trail-t a későbbi elemzésekhez.
        """
        filename = f"{sim_id}_{data['scenario']}.json"
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"[SIMULATOR] Results successfully saved to: {filepath}")
        except Exception as e:
            print(f"[SIMULATOR] CRITICAL ERROR saving results: {e}")

    def get_results(self, sim_id):
        """
        Eredmények visszakérése a memóriából (API híváshoz).
        """
        res = self.results_cache.get(sim_id)
        if not res:
            print(f"[SIMULATOR] Warning: Results for ID {sim_id} not found in cache.")
        return res